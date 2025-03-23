from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from uuid import uuid4

from ..helper.handlers import ErrorHandler
from ..helper.utils import login_required_401, restrict_roles_403, validate_username, get_request_data
from ..settings import EMAIL_HOST_USER

from ..models import Account, Invite

@csrf_exempt
def login(request):
    print("Raw Request Body:", request.body)  # Debugging line
    print("Request Headers:", request.headers)  # Debugging line
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["username", "password"], data
    )
    if not check.get("valid"):
        print("Error: Missing username or password")  # Debugging line
        return check.get("response")

    # check credentials
    user = authenticate(
        username=data["username"], password=data["password"])
    if user is None:
        print("Error: Invalid credentials")  # Debugging line
        return JsonResponse({
            "success": False,
            "description": "Data of user is invalid",
            "data": {},
        })

    auth_login(request, user)

    return JsonResponse({
        "success": True,
        "description": "User is logged in",
        "data": {
            "username": user.username,
            "role": "admin" if request.user.account.role == Account.ADMIN else "trainer" if request.user.account.role == Account.TRAINER else "player",
        },
    })


@login_required_401
def checklogin(request):
    return JsonResponse({
        "success": True,
        "description": "User is logged in",
        "data": {
            "username": request.user.username,
            "role": "admin" if request.user.account.role == Account.ADMIN else "trainer" if request.user.account.role == Account.TRAINER else "player",
        }
    })


@login_required_401
def logout(request):
    auth_logout(request)
    return JsonResponse({
        "success": True,
        "description": "User is logged out",
        "data": {},
    })


def register(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["password", "username", "new_user_token"], data
    )
    if not check.get("valid"):
        return check.get("response")

    # check if token is valid
    invite = Invite.objects.filter(uuid=data["new_user_token"]).first()
    if (invite is None):
        return JsonResponse({"success": False,
                             "description": "Token is not valid", "data": {}})

    # check if username is allowed
    if (not validate_username(data["username"])):
        return JsonResponse({"success": False,
                             "description": "Invalid username", "data": {}})

    if (User.objects.filter(
            username=data["username"]).exists()):
        return JsonResponse({"success": False,
                             "description": "Username already exists", "data": {}})

    newUser = User.objects.create_user(
        data["username"],
        invite.email,
        data["password"],
    )

    newUser.account = Account()
    newUser.save()

    if (invite.account.role == Account.ADMIN):
        newUser.account.role = Account.TRAINER
    else:
        newUser.account.role = Account.PLAYER

    newUser.account.save()

    invite.delete()

    login(request, newUser)

    return JsonResponse({"success": True,
                         "description": "User created", "data": {}})


@login_required_401
@restrict_roles_403([Account.ADMIN, Account.TRAINER])
def createUser(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["first_name", "last_name", "email", "url"], data
    )
    if not check.get("valid"):
        return check.get("response")

    token = str(uuid4())

    invite = Invite.objects.create(
        inviter=request.user,
        uuid=token,
        email=data["email"],
    )
    invite.save()

    # create and send mail
    html_message = render_to_string(
        "MomentumBackend/registrationEmail.html",
        {
            "full_name": f' {data["first_name"]} {data["last_name"]}',
            "account_type": "trainer"
            if request.user.account.role == Account.ADMIN
            else "user",
            "link": f'{data["url"]}/?new_user_token={token}',
        },
    )
    plain_message = strip_tags(html_message)
    addon = " "
    try:
        send_mail(
            "BachelorPraktikum Passwort",
            plain_message,
            EMAIL_HOST_USER,
            [data["email"]],
            html_message=html_message,
        )

    except:
        addon = " not"

    return JsonResponse({
        "success": True,
        "description": "email with invite was" + addon + " sent",
        "data": {"new_user_token": token},
    })


@login_required_401
# admin accs can not be deleted
@restrict_roles_403([Account.TRAINER, Account.PLAYER])
def deleteAccount(request):
    request.user.delete()

    return JsonResponse({
        "success": True,
        "description": "User was successfully deleted",
        "data": {},
    })


@login_required_401
def changeLanguage(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["language"], data
    )
    if not check.get("valid"):
        return check.get("response")

    request.user.account.language = data["language"]
    request.user.account.save()

    return JsonResponse({
        "success": True,
        "description": "Language changed successfully.",
        "data": {},
    })


@login_required_401
def getLanguage(request):
    return JsonResponse({
        "success": True,
        "description": "Returning language.",
        "data": {"language": request.user.account.language},
    })


@login_required_401
@restrict_roles_403([Account.TRAINER])
def getTrainersUsers(request):
    # get users of trainer
    users = User.objects.filter(account__trainer=request.user)
    user_data = []
    for user in users:
        # TODO: get percentage of done exercises
        perc_done = 0
        user_data.append(
            {
                "id": user.id,
                "username": user.username,
                "plan": user.account.plan.id if user.account.plan else None,
                "done_exercises": perc_done,
            }
        )

    return JsonResponse({
        "success": True,
        "description": "Returning users",
        "data": {"users": user_data},
    })


@login_required_401
@restrict_roles_403([Account.ADMIN])
def getTrainers(request):
    # get all trainers
    trainers = User.objects.filter(account__role=Account.TRAINER)
    trainer_data = []
    for trainer in trainers:
        trainer_data.append(
            {
                "id": trainer.id,
                "username": trainer.username,
            }
        )

    return JsonResponse({
        "success": True,
        "description": "Returning all trainers",
        "data": {"trainers": trainer_data},
    })


@login_required_401
@restrict_roles_403([Account.ADMIN])
def deleteTrainer(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["id"], data
    )
    if not check.get("valid"):
        return check.get("response")

    # check if trainer exists
    if not User.objects.filter(id=data["id"], account__role=Account.TRAINER).exists():
        return JsonResponse({"success": False,
                             "description": "Trainer not found", "data": {}})

    # delete trainer
    User.objects.filter(
        id=data["id"], account__role=Account.TRAINER).delete()
    return JsonResponse({"success": True,
                         "description": "Trainer was deleted", "data": {}})


@login_required_401
@restrict_roles_403([Account.ADMIN, Account.TRAINER])
def deleteUser(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["id"], data
    )
    if not check.get("valid"):
        return check.get("response")

    # check if user exists
    if not User.objects.filter(id=data["id"]).exists():
        return JsonResponse({"success": False,
                             "description": "User not found", "data": {}})

    # check if trainer is allowed to delete this user
    if request.user.account.role == Account.TRAINER:
        if not User.objects.filter(id=data["id"], trainer=request.user).exists():
            return JsonResponse({
                "success": False,
                "description": "Trainers can only delete user assigned to them",
                "data": {},
            })

    # delete user
    User.objects.filter(id=data["id"]).delete()
    return JsonResponse({"success": True, "description": "User was deleted", "data": {}})


@login_required_401
@restrict_roles_403([Account.ADMIN, Account.TRAINER])
def getInvited(request):
    invites = Invite.objects.filter(inviter=request.user)
    invite_data = []
    for invite in invites:
        invite_data.append(
            {
                "id": invite.id,
                "email": invite.email,
            }
        )
    return JsonResponse({
        "success": True,
        "description": "Returning created invites",
        "data": {"invited": invite_data},
    })


@login_required_401
@restrict_roles_403([Account.ADMIN, Account.TRAINER])
def cancelInvite(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["id"], data
    )
    if not check.get("valid"):
        return check.get("response")

    # check if invite exists
    if not Invite.objects.filter(id=data["id"], inviter=request.user).exists():
        return JsonResponse({
            "success": False,
            "description": "Failed to cancel invite.",
            "data": {},
        })

    # delete invite
    Invite.objects.filter(id=data["id"]).delete()
    return JsonResponse({"success": True,
                         "description": "Token invalidated", "data": {}})


@login_required_401
def changeUsername(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["username"], data
    )
    if not check.get("valid"):
        return check.get("response")

    # check validity
    if not validate_username(data["username"]):
        return JsonResponse({"success": False,
                             "description": "username invalid", "data": {}})

    # check if username is not already uesd
    if (User.objects.filter(username=data["username"]).exists()):
        return JsonResponse({
            "success": False,
            "description": "Username already used",
            "data": {},
        })

    # change username
    request.user.username = data["username"]
    request.user.save()

    return JsonResponse({
        "success": True,
        "description": "Usernamed changed.",
        "data": {},
    })


@login_required_401
def changePassword(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["password", "new_password"], data
    )
    if not check.get("valid"):
        return check.get("response")

    # check password
    user = authenticate(
        username=request.user.username, password=data["password"]
    )
    if user is None:
        return JsonResponse({"success": False,
                             "description": "Incorrect password.", "data": {}})

    # change password
    user.set_password(data["new_password"])
    user.save()
    # creating tokens

    return JsonResponse({
        "success": True,
        "description": "Password changed.",
        "data": {},
    })


@login_required_401
@restrict_roles_403([Account.PLAYER])
def changeAvatar(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["avatar"], data
    )
    if not check.get("valid"):
        return check.get("response")

    avatarHairStyle = int(data["avatar"]["hairStyle"])
    avatarHairColor = int(data["avatar"]["hairColor"])
    avatarSkinColor = int(data["avatar"]["skinColor"])
    avatarEyeColor = int(data["avatar"]["eyeColor"])
    # checking if number is small enough to fit in data base
    if avatarHairStyle >= 100000 or avatarHairColor >= 100000 or avatarSkinColor >= 100000 or avatarEyeColor >= 100000:
        return JsonResponse({"success": False,
                             "description": "invalid value", "data": {}})
    # chaneg avatar
    request.user.account.avatarHairStyle = avatarHairStyle
    request.user.account.avatarHairColor = avatarHairColor
    request.user.account.avatarSkinColor = avatarSkinColor
    request.user.account.avatarEyeColor = avatarEyeColor
    request.user.account.save()
    return JsonResponse({"success": True, "description": "Avatar changed", "data": {}})


@login_required_401
@restrict_roles_403([Account.PLAYER])
def getProfile(request):
    # get profile data
    return JsonResponse({
        "success": True,
        "description": "Returning profile data",
        "data": {
            "username": request.user.username,
            "avatar": {
                "hairStyle": request.user.account.avatarHairStyle,
                "hairColor": request.user.account.avatarHairColor,
                "skinColor": request.user.account.avatarSkinColor,
                "eyeColor": request.user.account.avatarEyeColor,
            },
            "motivation": request.user.account.motivation,
        }
    })


@login_required_401
def changeMotivation(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["motivation"], data
    )
    if not check.get("valid"):
        return check.get("response")

    # change motivation
    request.user.account.motivation = data["motivation"]
    request.user.account.save()
    return JsonResponse({"success": True,
                         "description": "Motivation changed", "data": {}})


def sendPasswordResetEmail(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["username", "url"], data
    )
    if not check.get("valid"):
        return check.get("response")

    # get user from database
    user: User = None
    if (user := User.objects.filter(username=data["username"]).first()) is not None:

        form = PasswordResetForm({"email": user.email})

        # TODO: add proper txt email template
        # TODO: add subject template
        if form.is_valid():
            form.save(
                domain_override=data['url'],
                email_template_name="MomentumBackend/resetEmail.html",
                html_email_template_name="MomentumBackend/resetEmail.html",
                extra_email_context={
                    "full_name": f" {user.first_name} {user.last_name}",
                    "link": f"{data['url'].rstrip('/')}/?username={data['username']}&reset_token=",
                }
            )

    return JsonResponse({
        "success": True,
        "description": "Reset E-mail was sent.",
        "data": {},
    })


def resetPassword(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["username", "reset_token", "new_password"], data)
    if not check.get("valid"):
        return check.get("response")

    user = User.objects.filter(username=data["username"]).first()

    if user is None:
        return JsonResponse({"success": False,
                             "description": "Username is not used", "data": {}})

    if not default_token_generator.check_token(user, data["reset_token"]):
        return JsonResponse({"success": False,
                             "description": "Reset token is invalid", "data": {}})

    # update the password
    user.set_password(data["new_password"])
    user.save()

    return JsonResponse({"success": True,
                         "description": "Password reset.", "data": {}})
