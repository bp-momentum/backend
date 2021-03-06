from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from ..Helperclasses.jwttoken import JwToken
from ..Helperclasses.handlers import (
    FULL_COMBO,
    DateHandler,
    ErrorHandler,
    InvitationsHandler,
    PasswordHandler,
    TrainerHandler,
    UserHandler,
)
import hashlib
import datetime

from ..serializers import CreateTrainerSerializer, CreateUserSerializer
from ..models import Leaderboard, Location, OpenToken, User, Trainer, Admin

MAX_LEVEL = 200
MULT_PER_LVL = 1.25
FIRST_LVL = 300


# creating random password
from ..settings import EMAIL_HOST_USER

USERNAME_LENGTH = 50
FIRST_NAME_LENGTH = 50
LAST_NAME_LENGTH = 50
EMAIL_LENGTH = 254
STREET_LENGTH = 128
POSTAL_CODE_LENGTH = 12
TELEPHONE_LENGTH = 50
CITY_LENGTH = 128
COUNTRY_LENGTH = 64
LANGUAGE_LENGTH = 50
ACADEMIA_LENGTH = 50
ADDRESS_ADD_LENGTH = 128
H_NR_LENGTH = 12
MOTIVATION_LENGTH = 1000
MIN_USERNAME_LENGTH = 3
ALLOWED = "1234567890qwertzuiopasdfghjklyxcvbnmQWERTZUIOPASDFGHJKLYXCVBNM _-"


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            [],
            request.headers,
            ["password", "username", "new_user_token"],
            request.data,
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        req_data["password"] = str(
            hashlib.sha3_256(req_data["password"].encode("utf8")).hexdigest()
        )
        token = JwToken.check_new_user_token(req_data["new_user_token"])
        # check if token is valid
        if (not token["valid"]) or (
            not OpenToken.objects.filter(token=req_data["new_user_token"]).exists()
        ):
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        # check if username is allowed
        if (
            (not all(c in ALLOWED for c in req_data["username"]))
            or len(req_data["username"]) < MIN_USERNAME_LENGTH
            or str(req_data["username"]).startswith(" ")
        ):
            data = {"success": False, "description": "Invalid username", "data": {}}
            return Response(data)

        # check account type
        req_data["first_name"] = token["info"]["first_name"]
        req_data["last_name"] = token["info"]["last_name"]
        req_data["email_address"] = token["info"]["email_address"]
        if token["info"]["create_account_type"] == "user":
            trainer_id = Trainer.objects.get(username=token["info"]["initiator"]).id
            req_data["trainer"] = trainer_id
            today = datetime.datetime.now()
            first_login = DateHandler.get_string_of_date(
                today.day, today.month, today.year
            )
            req_data["first_login"] = first_login
            serializer = CreateUserSerializer(data=req_data)

        elif token["info"]["create_account_type"] == "trainer":
            serializer = CreateTrainerSerializer(data=req_data)

        else:
            data = {
                "success": False,
                "description": "account type cannot create a new account",
                "data": {},
            }
            return Response(data)

        # trainer creates new User

        if serializer.is_valid():
            # check if username already exists
            if (
                not User.objects.filter(username=request.data["username"]).exists()
                and not Trainer.objects.filter(
                    username=request.data["username"]
                ).exists()
                and not Admin.objects.filter(username=request.data["username"]).exists()
            ):

                # save User in the databank
                serializer.save()

                # add user to leaderboard with score of 0
                if token["info"]["create_account_type"] == "user":
                    Leaderboard.objects.create(
                        user=User.objects.get(username=request.data["username"]),
                        score=0,
                    )

                # creating the session_token
                session_token = JwToken.create_session_token(
                    req_data["username"], token["info"]["create_account_type"]
                )
                refresh_token = JwToken.create_refresh_token(
                    req_data["username"], token["info"]["create_account_type"], True
                )
                data = {
                    "success": True,
                    "description": "User was created",
                    "data": {
                        "session_token": session_token,
                        "refresh_token": refresh_token,
                    },
                }

                OpenToken.objects.filter(token=req_data["new_user_token"]).delete()
                UserHandler.last_login(req_data["username"])

                return Response(data)
            else:
                data = {
                    "success": False,
                    "description": "Username already exists",
                    "data": {},
                }

                return Response(data)

        return Response(serializer.errors)


class CreateUserView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"],
            request.headers,
            ["first_name", "last_name", "email_address", "url"],
            request.data,
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)

        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        # check if arguments are fine
        if not ErrorHandler.check_input_length(
            req_data["first_name"], FIRST_NAME_LENGTH
        ):
            return ErrorHandler.length_wrong_response("first name")
        if not ErrorHandler.check_input_length(req_data["last_name"], LAST_NAME_LENGTH):
            return ErrorHandler.length_wrong_response("last name")
        if not ErrorHandler.check_input_length(req_data["email_address"], EMAIL_LENGTH):
            return ErrorHandler.length_wrong_response("email address")

        info = token["info"]

        # check account type and create new-user-token
        if info["account_type"] == "admin":
            new_user_token = JwToken.create_new_user_token(
                info["username"],
                req_data["first_name"],
                req_data["last_name"],
                req_data["email_address"],
                "trainer",
            )
        elif info["account_type"] == "trainer":
            new_user_token = JwToken.create_new_user_token(
                info["username"],
                req_data["first_name"],
                req_data["last_name"],
                req_data["email_address"],
                "user",
            )
        else:
            data = {
                "success": False,
                "description": "account type is not allowed to add new users",
                "data": {},
            }

            return Response(data)
        # create data base entry
        OpenToken.objects.create(
            token=new_user_token,
            email=req_data["email_address"],
            first_name=req_data["first_name"],
            last_name=req_data["last_name"],
            creator=info["username"],
        )
        # create and send mail
        html_message = render_to_string(
            "MomentumBackend/registrationEmail.html",
            {
                "full_name": f' {req_data["first_name"]} {req_data["last_name"]}',
                "account_type": "trainer"
                if info["account_type"] == "admin"
                else "user",
                "link": f'{req_data["url"]}/?new_user_token={new_user_token}',
            },
        )
        plain_message = strip_tags(html_message)
        addon = " "
        try:
            send_mail(
                "BachelorPraktikum Passwort",
                plain_message,
                EMAIL_HOST_USER,
                [req_data["email_address"]],
                html_message=html_message,
            )

        except:
            addon = " not"
        data = {
            "success": True,
            "description": "email with invite was" + addon + " sent",
            "data": {"new_user_token": new_user_token},
        }

        return Response(data)


class LoginView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            [], request.headers, ["username", "password"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        # check password
        passcheck = PasswordHandler.check_password(
            req_data["username"], req_data["password"]
        )
        if passcheck == "invalid":
            data = {
                "success": False,
                "description": "Data of user is invalid",
                "data": {},
            }

            return Response(data)

        # create session- and refresh-token
        session_token = JwToken.create_session_token(req_data["username"], passcheck)
        refresh_token = JwToken.create_refresh_token(
            req_data["username"], passcheck, False
        )
        data = {
            "success": True,
            "description": "User is logged in",
            "data": {"session_token": session_token, "refresh_token": refresh_token},
        }

        UserHandler.last_login(req_data["username"])

        return Response(data)


class LogoutAllDevicesView(APIView):
    def post(self, request, *args, **kqargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]
        # create new tokens
        JwToken.invalidate_session_token(info["username"])
        session_token = JwToken.create_session_token(
            username=info["username"], account_type=info["account_type"]
        )
        refresh_token = JwToken.create_refresh_token(
            username=info["username"], account_type=info["account_type"], set_pswd=True
        )
        data = {
            "success": True,
            "description": "refresh-token changed",
            "data": {"session_token": session_token, "refresh_token": refresh_token},
        }

        return Response(data)


class AuthView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            [], request.headers, ["refresh_token"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = request.data["refresh_token"]
        info = JwToken.check_refresh_token(token)
        # check if token is valid
        if not info["valid"]:
            data = {
                "success": False,
                "description": "refresh-token invalid",
                "data": {},
            }

            return Response(data)

        # create new tokens
        session_token = JwToken.create_session_token(
            username=info["info"]["username"], account_type=info["info"]["account_type"]
        )
        refresh_token = JwToken.create_refresh_token(
            username=info["info"]["username"],
            account_type=info["info"]["account_type"],
            set_pswd=False,
        )
        data = {
            "success": True,
            "description": "user is now logged in",
            "data": {"session_token": session_token, "refresh-token": refresh_token},
        }

        UserHandler.last_login(info["info"]["username"])

        return Response(data)


class DeleteAccountView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        # delete user
        if User.objects.filter(username=info["username"]).exists():
            User.objects.filter(username=info["username"]).delete()
        elif Trainer.objects.filter(username=info["username"]).exists():
            Trainer.objects.filter(username=info["username"]).delete()
        elif Admin.objects.filter(username=info["username"]).exists():
            # admins can not be deleted
            data = {
                "success": False,
                "description": "Admin account can not be deleted",
                "data": {},
            }

            return Response(data)
        else:
            data = {"success": False, "description": "User not found", "data": {}}

            return Response(data)
        data = {
            "success": True,
            "description": "User was successfully deleted",
            "data": {},
        }

        return Response(data)


class ChangeLanguageView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["language"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = request.headers["Session-Token"]
        token_data = JwToken.check_session_token(token)
        # check if token is valid
        if not token_data["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}

            return Response(data)

        info = token_data["info"]

        # change language
        if not UserHandler.set_user_language(
            info["username"], req_data["language"], LANGUAGE_LENGTH
        ):
            data = {
                "success": False,
                "description": "language could not be changed",
                "data": {},
            }
        else:
            data = {
                "success": True,
                "description": "language was successfully changed",
                "data": {},
            }

        return Response(data)


class GetLanguageView(APIView):
    def get(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = request.headers["Session-Token"]
        token_data = JwToken.check_session_token(token)
        # check if token is valid
        if not token_data["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}

            return Response(data)

        info = token_data["info"]

        # get language
        res = UserHandler.get_user_language(info["username"])
        # check if valid
        if res == None:
            data = {"success": False, "description": "user not found", "data": {}}
        else:
            data = {
                "success": True,
                "description": "language returned",
                "data": {"language": res},
            }

        return Response(data)


class GetUsersOfTrainerView(APIView):
    def get(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        # check if request is from trainer
        if not info["account_type"] == "trainer":
            data = {
                "success": False,
                "description": "Only Trainers are allowed to see their users",
                "data": {},
            }
            return Response(data)

        # get users of trainer
        trainer = Trainer.objects.get(username=info["username"])
        users = User.objects.filter(trainer=trainer)
        users_data = UserHandler.get_users_data_for_upper(users)
        data = {
            "success": True,
            "description": "Returning users",
            "data": {"users": users_data},
        }
        return Response(data)

    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["id"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        # check if request is from admin
        if not info["account_type"] == "admin":
            data = {
                "success": False,
                "description": "Only admins can get other trainers users",
                "data": {},
            }
            return Response(data)

        # check if trainer exists
        if not Trainer.objects.filter(id=req_data["id"]).exists():
            data = {"success": False, "description": "Trainer not found", "data": {}}
            return Response(data)

        # get users of requested trainer
        trainer = Trainer.objects.get(id=req_data["id"])
        users = User.objects.filter(trainer=trainer)
        users_data = UserHandler.get_users_data_for_upper(users)

        data = {
            "success": True,
            "description": "Returned users of trainer",
            "data": {"users": users_data},
        }
        return Response(data)


class GetTrainersView(APIView):
    def get(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        # check if requested by admin
        if not info["account_type"] == "admin":
            data = {
                "success": False,
                "description": "Only Admins are allowed to see trainers",
                "data": {},
            }
            return Response(data)

        # get all trainers
        trainers = Trainer.objects.all()
        trainers_data = TrainerHandler.get_trainers_data(trainers)

        data = {
            "success": True,
            "description": "Returning all trainers",
            "data": {"trainers": trainers_data},
        }
        return Response(data)


class DeleteTrainerView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["id"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        # check if requested by admin
        if not info["account_type"] == "admin":
            data = {
                "success": False,
                "description": "Only admins can delete trainers",
                "data": {},
            }
            return Response(data)

        # check if trainer exists
        if not Trainer.objects.filter(id=req_data["id"]).exists():
            data = {"success": False, "description": "Trainer not found", "data": {}}
            return Response(data)

        # delete trainer
        Trainer.objects.filter(id=req_data["id"]).delete()
        data = {"success": True, "description": "Trainer was deleted", "data": {}}
        return Response(data)


class DeleteUserView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["id"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        # check if requested by admin or trainer
        if not (info["account_type"] == "admin" or info["account_type"] == "trainer"):
            data = {
                "success": False,
                "description": "Only admins and trainers can delete user",
                "data": {},
            }
            return Response(data)

        # check if user exists
        if not User.objects.filter(id=req_data["id"]).exists():
            data = {"success": False, "description": "User not found", "data": {}}
            return Response(data)

        # check if trainer is allowed to delete this user
        if info["account_type"] == "trainer":
            trainer: Trainer = Trainer.objects.get(username=info["username"])
            if not User.objects.filter(id=req_data["id"], trainer=trainer).exists():
                data = {
                    "success": False,
                    "description": "Trainers can only delete user assigned to them",
                    "data": {},
                }
                return Response(data)

        # delete user
        User.objects.filter(id=req_data["id"]).delete()
        data = {"success": True, "description": "User was deleted", "data": {}}
        return Response(data)


class GetUserLevelView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["username"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        if not User.objects.filter(username=req_data["username"]).exists():
            data = {"success": False, "description": "User not found", "data": {}}
            return Response(data)

        user: User = User.objects.get(username=req_data["username"])
        res = UserHandler.calc_level(user.xp, MAX_LEVEL)
        data = {
            "success": True,
            "description": "returning level and progress of next level",
            "data": {"level": res[0], "progress": res[1]},
        }
        return Response(data)


class GetInvitedView(APIView):
    def get(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        open_tokens = OpenToken.objects.filter(creator=info["username"])
        invites = InvitationsHandler.get_invited_data(open_tokens)
        data = {
            "success": True,
            "description": "Returning created invites",
            "data": {"invited": invites},
        }
        return Response(data)


class InvalidateInviteView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["id"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        if not OpenToken.objects.filter(
            id=req_data["id"], creator=info["username"]
        ).exists():
            data = {
                "success": False,
                "description": "Invalid invite or not allowed to invalidate",
                "data": {},
            }
            return Response(data)

        OpenToken.objects.filter(id=req_data["id"], creator=info["username"]).delete()
        data = {"success": True, "description": "Token invalidated", "data": {}}
        return Response(data)


class ChangeUsernameView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["username"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        # check if length is fine
        if (
            not ErrorHandler.check_input_length(req_data["username"], USERNAME_LENGTH)
            or (not all(c in ALLOWED for c in req_data["username"]))
            or len(req_data["username"]) < MIN_USERNAME_LENGTH
            or str(req_data["username"]).startswith(" ")
        ):
            data = {"success": False, "description": "username invalid", "data": {}}
            return Response(data)

        # check if first symbol is space
        if str(req_data["username"]).startswith(" "):
            data = {"success": False, "description": "Invalid username", "data": {}}
            return Response(data)

        info = token["info"]

        # get correct user
        if info["account_type"] == "user":
            user: User = User.objects.get(username=info["username"])
        elif info["account_type"] == "trainer":
            user: Trainer = Trainer.objects.get(username=info["username"])
        elif info["account_type"] == "admin":
            user: Admin = Admin.objects.get(username=info["username"])

        # check if username is not already uesd
        if (
            User.objects.filter(username=req_data["username"]).exists()
            or Trainer.objects.filter(username=req_data["username"]).exists()
            or Admin.objects.filter(username=req_data["username"]).exists()
        ):
            data = {
                "success": False,
                "description": "Username already used",
                "data": {},
            }
            return Response(data)

        # change username
        user.username = req_data["username"]
        user.save(force_update=True)
        # creating tokens
        session_token = JwToken.create_session_token(
            req_data["username"], info["account_type"]
        )
        refresh_token = JwToken.create_refresh_token(
            req_data["username"], info["account_type"], True
        )
        data = {
            "success": True,
            "description": "Usernamed changed",
            "data": {"session_token": session_token, "refresh_token": refresh_token},
        }
        return Response(data)


class ChangePasswordView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"],
            request.headers,
            ["password", "new_password"],
            request.data,
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]
        # get correct user
        if info["account_type"] == "user":
            user: User = User.objects.get(username=info["username"])
        elif info["account_type"] == "trainer":
            user: Trainer = Trainer.objects.get(username=info["username"])
        elif info["account_type"] == "admin":
            user: Admin = Admin.objects.get(username=info["username"])

        # logout on all devices
        response = LogoutAllDevicesView.post(LogoutAllDevicesView, request)
        if not response.data.get("success"):
            return response

        # check password
        if (
            PasswordHandler.check_password(user.username, req_data["password"])
            != info["account_type"]
        ):
            data = {"success": False, "description": "incorrect password", "data": {}}
            return Response(data)

        # change password
        user.password = str(
            hashlib.sha3_256(req_data["new_password"].encode("utf8")).hexdigest()
        )
        user.save(force_update=True)
        # creating tokens
        session_token = JwToken.create_session_token(
            info["username"], info["account_type"]
        )
        refresh_token = JwToken.create_refresh_token(
            info["username"], info["account_type"], True
        )
        data = {
            "success": True,
            "description": "Password changed",
            "data": {"session_token": session_token, "refresh_token": refresh_token},
        }
        return Response(data)


class ChangeAvatarView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["avatar"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        # check if it is a user
        if not info["account_type"] == "user":
            data = {
                "success": False,
                "description": "Only users can change their avatar",
                "data": {},
            }
            return Response(data)

        user: User = User.objects.get(username=info["username"])

        avatarHairStyle = int(req_data["avatar"]["hairStyle"])
        avatarHairColor = int(req_data["avatar"]["hairColor"])
        avatarSkinColor = int(req_data["avatar"]["skinColor"])
        avatarEyeColor = int(req_data["avatar"]["eyeColor"])
        # checking if number is small enough to fit in data base
        if avatarHairStyle >= 100000 or avatarHairColor >= 100000 or avatarSkinColor >= 100000 or avatarEyeColor >= 100000:
            data = {"success": False, "description": "invalid value", "data": {}}
            return Response(data)
        # chaneg avatar
        user.avatarHairStyle = avatarHairStyle
        user.avatarHairColor = avatarHairColor
        user.avatarSkinColor = avatarSkinColor
        user.avatarEyeColor = avatarEyeColor
        user.save(force_update=True)
        data = {"success": True, "description": "Avatar changed", "data": {}}
        return Response(data)


class GetProfileView(APIView):
    def get(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]
        # check if it is a user
        if not info["account_type"] == "user":
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        user: User = User.objects.get(username=info["username"])
        # get profile data
        data = {
            "success": True,
            "description": "Returning profile data",
            "data": UserHandler.get_profile_data(user),
        }
        return Response(data)


class GetTrainerContactView(APIView):
    def get(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        # check if request by user
        if not (info["account_type"] == "user" or info["account_type"] == "trainer"):
            data = {
                "success": False,
                "description": "Only users can request their trainers contact and trainers their own one",
                "data": {},
            }
            return Response(data)
        if info["account_type"] == "user":
            user: User = User.objects.get(username=info["username"])
            # get trainer of user
            trainer: Trainer = user.trainer
            description = "Returning contact data of trainer"
        elif info["account_type"] == "trainer":
            trainer = Trainer.objects.get(username=info["username"])
            description = "Returning your contact data"
        # get contact data of the trainer
        data = {
            "success": True,
            "description": description,
            "data": TrainerHandler.get_trainer_contact(
                trainer, info["account_type"] == "user"
            ),
        }
        return Response(data)


class SetTrainerLocationView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"],
            request.headers,
            ["street", "postal_code", "country", "city", "house_nr", "address_add"],
            request.data,
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        # check length
        if not ErrorHandler.check_input_length(req_data["street"], STREET_LENGTH):
            return ErrorHandler.length_wrong_response("Name of street")
        if not ErrorHandler.check_input_length(
            req_data["postal_code"], POSTAL_CODE_LENGTH
        ):
            return ErrorHandler.length_wrong_response("postal code")
        if not ErrorHandler.check_input_length(req_data["country"], COUNTRY_LENGTH):
            return ErrorHandler.length_wrong_response("Name of country")
        if not ErrorHandler.check_input_length(req_data["city"], CITY_LENGTH):
            return ErrorHandler.length_wrong_response("Name of city")
        if not ErrorHandler.check_input_length(req_data["house_nr"], H_NR_LENGTH):
            return ErrorHandler.length_wrong_response("house number")
        if not ErrorHandler.check_input_length(
            req_data["address_add"], ADDRESS_ADD_LENGTH
        ):
            return ErrorHandler.length_wrong_response("Address addition")

        info = token["info"]

        # check if requested by trainer
        if not info["account_type"] == "trainer":
            data = {"success": False, "description": "Not a trainer", "data": {}}
            return Response(data)

        trainer: Trainer = Trainer.objects.get(username=info["username"])
        # create or get location
        if not Location.objects.filter(
            street=req_data["street"],
            postal_code=req_data["postal_code"],
            country=req_data["country"],
            city=req_data["city"],
            house_nr=req_data["house_nr"],
            address_addition=req_data["address_add"],
        ).exists():
            loc: Location = Location.objects.create(
                street=req_data["street"],
                postal_code=req_data["postal_code"],
                country=req_data["country"],
                city=req_data["city"],
                house_nr=req_data["house_nr"],
                address_addition=req_data["address_add"],
            )
        else:
            loc: Location = Location.objects.get(
                street=req_data["street"],
                postal_code=req_data["postal_code"],
                country=req_data["country"],
                city=req_data["city"],
                house_nr=req_data["house_nr"],
                address_addition=req_data["address_add"],
            )
        # change location
        trainer.location = loc
        trainer.save(force_update=True)
        data = {"success": True, "description": "Location updated", "data": {}}
        return Response(data)


class ChangeTrainerTelephoneView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["telephone"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        # check length
        if not ErrorHandler.check_input_length(req_data["telephone"], TELEPHONE_LENGTH):
            return ErrorHandler.length_wrong_response("telephone numer")

        info = token["info"]

        # check if requested by trainer
        if not info["account_type"] == "trainer":
            data = {"success": False, "description": "Not a trainer", "data": {}}
            return Response(data)

        trainer: Trainer = Trainer.objects.get(username=info["username"])
        # change telephone number
        trainer.telephone = req_data["telephone"]
        trainer.save(force_update=True)
        data = {"success": True, "description": "Telephone number updated", "data": {}}
        return Response(data)


class ChangeTrainerAcademiaView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["academia"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        # check length
        if not ErrorHandler.check_input_length(req_data["academia"], ACADEMIA_LENGTH):
            return ErrorHandler.length_wrong_response("academia")

        info = token["info"]

        # check if requested by trainer
        if not info["account_type"] == "trainer":
            data = {"success": False, "description": "Not a trainer", "data": {}}
            return Response(data)

        trainer: Trainer = Trainer.objects.get(username=info["username"])
        # change academia
        trainer.academia = req_data["academia"]
        trainer.save(force_update=True)
        data = {"success": True, "description": "Academia updated", "data": {}}
        return Response(data)


class ChangeMotivationView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["motivation"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        # check length
        if not ErrorHandler.check_input_length(
            req_data["motivation"], MOTIVATION_LENGTH
        ):
            return ErrorHandler.length_wrong_response("Motivation")

        info = token["info"]

        # check if request by user
        if not info["account_type"] == "user":
            data = {
                "success": False,
                "description": "Only users can change their motivation",
                "data": {},
            }
            return Response(data)

        user: User = User.objects.get(username=info["username"])

        # change motivation
        user.motivation = req_data["motivation"]
        user.save(force_update=True)
        data = {"success": True, "description": "Motivation changed", "data": {}}
        return Response(data)


class SearchUserView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, ["search"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]
        users = User.objects.filter(username__icontains=req_data["search"]).exclude(
            username=info["username"]
        )
        users_data = UserHandler.get_users_data(users)

        data = {
            "success": True,
            "description": "returning list of matching users",
            "data": {"users": users_data},
        }
        return Response(data)


class GetListOfUsers(APIView):
    def get(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        users = User.objects.exclude(username=info["username"])
        users_data = UserHandler.get_users_data(users)

        data = {
            "success": True,
            "description": "returning list of users",
            "data": {"users": users_data},
        }
        return Response(data)


class GetStreakView(APIView):
    def get(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            ["Session-Token"], request.headers, [], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        token = JwToken.check_session_token(request.headers["Session-Token"])
        # check if token is valid
        if not token["valid"]:
            data = {"success": False, "description": "Token is not valid", "data": {}}
            return Response(data)

        info = token["info"]

        # only users can get their own achievements
        if not User.objects.filter(username=info["username"]).exists():
            data = {"success": False, "description": "Not a user", "data": {}}
            return Response(data)

        user: User = User.objects.get(username=info["username"])

        data = {
            "success": True,
            "description": "returning streak",
            "data": {
                "days": user.streak,
                "flame_glow": UserHandler.check_flame_glow(user),
                "flame_height": user.streak / FULL_COMBO
                if user.streak <= FULL_COMBO
                else 1.0,
            },
        }
        return Response(data)


class GetPasswordResetEmailView(APIView):
    def post(self, request, *args, **kwargs):
        # checking if it contains all arguments
        check = ErrorHandler.check_arguments(
            [], request.headers, ["username", "url"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)

        req_data = dict(request.data)

        # get user from database
        user: User = None
        if User.objects.filter(username=req_data["username"]).exists():
            user = User.objects.get(username=req_data["username"])
        else:
            data = {"success": False, "description": "Username is not used", "data": {}}
            return Response(data)

        # get url from frontend and style email
        url = req_data["url"]

        # create the reset token
        reset_token = JwToken.create_reset_password_token(user.username)
        html_message = render_to_string(
            "MomentumBackend/resetEmail.html",
            {
                "full_name": f" {user.first_name} {user.last_name}",
                "link": f"{url}/?reset_token={reset_token}",
            },
        )
        plain_message = strip_tags(html_message)

        # send email
        try:
            send_mail(
                "BachelorPraktikum Passwort",
                plain_message,
                EMAIL_HOST_USER,
                [user.email_address],
                html_message=html_message,
            )
            data = {
                "success": True,
                "description": "email with invite was sent",
                "data": {},
            }
        except Exception as e:
            data = {
                "success": False,
                "description": "email with invite was not sent",
                "data": {e},
            }

        return Response(data)


class SetPasswordResetEmailView(APIView):
    def post(self, request, *args, **kwargs):
        # check if all arguments are there
        check = ErrorHandler.check_arguments(
            [], request.headers, ["reset_token", "new_password"], request.data
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        req_data = dict(request.data)
        # check the reset_token
        reset_token = JwToken.check_reset_password_token(req_data["reset_token"])

        if not reset_token["valid"]:
            data = {
                "success": False,
                "description": "Reset token is not valid",
                "data": {},
            }
            return Response(data)
        info = reset_token["info"]
        user: User = None
        if User.objects.filter(username=info["username"]).exists():
            user = User.objects.get(username=info["username"])
        else:
            data = {"success": False, "description": "Username is not used", "data": {}}
            return Response(data)

        # update the password
        user.password = str(
            hashlib.sha3_256(req_data["new_password"].encode("utf8")).hexdigest()
        )
        user.save(force_update=True)

        data = {"success": True, "description": "Password got reset", "data": {}}
        return Response(data)
