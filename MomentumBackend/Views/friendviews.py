from rest_framework.views import APIView
from rest_framework.response import Response

from ..Helperclasses.jwttoken import JwToken
from ..Helperclasses.handlers import ErrorHandler, FriendHandler

from ..models import Friends, User
from ..serializers import CreateFriends


class GetMyFriendsView(APIView):
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

        # must be user
        if not User.objects.filter(username=info["username"]).exists():
            data = {"success": False, "description": "Not a user", "data": {}}
            return Response(data)

        user: User = User.objects.get(username=info["username"])
        friends = FriendHandler.get_friends(user)
        data = {
            "success": True,
            "description": "returning friends",
            "data": {"friends": friends},
        }
        return Response(data)


class GetPendingRequestView(APIView):
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

        # must be user
        if not User.objects.filter(username=info["username"]).exists():
            data = {"success": False, "description": "Not a user", "data": {}}
            return Response(data)

        user: User = User.objects.get(username=info["username"])
        pending = FriendHandler.get_pending_requests(user)
        data = {
            "success": True,
            "description": "returning pending requests",
            "data": {"pending": pending},
        }
        return Response(data)


class GetRequestView(APIView):
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

        # must be user
        if not User.objects.filter(username=info["username"]).exists():
            data = {"success": False, "description": "Not a user", "data": {}}
            return Response(data)

        user: User = User.objects.get(username=info["username"])
        requests = FriendHandler.get_requests(user)
        data = {
            "success": True,
            "description": "returning requests",
            "data": {"requests": requests},
        }
        return Response(data)


class AddFriendView(APIView):
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

        # must be user
        if not User.objects.filter(username=info["username"]).exists():
            data = {"success": False, "description": "Not a user", "data": {}}
            return Response(data)

        # check if self
        if info["username"] == req_data["username"]:
            data = {
                "success": False,
                "description": "Can not add yourself as a friend",
                "data": {},
            }
            return Response(data)
        # added must be user/exist
        if not User.objects.filter(username=req_data["username"]).exists():
            data = {
                "success": False,
                "description": "Does not exist or is not a user",
                "data": {},
            }
            return Response(data)

        # check if already friends
        is_from: User = User.objects.get(username=info["username"])
        is_to: User = User.objects.get(username=req_data["username"])
        if FriendHandler.already_friends(is_from, is_to):
            data = {"success": False, "description": "Already friends", "data": {}}
            return Response(data)
        request_data = {"friend1": is_from.id, "friend2": is_to.id}
        serializer = CreateFriends(data=request_data)
        if not serializer.is_valid():
            data = {
                "success": False,
                "description": "invalid data",
                "data": {"error": serializer.error_messages},
            }
            return Response(data)

        serializer.save()
        data = {"success": True, "description": "Request sent", "data": {}}
        return Response(data)


class AcceptRequestView(APIView):
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

        # must be user
        if not User.objects.filter(username=info["username"]).exists():
            data = {"success": False, "description": "Not a user", "data": {}}
            return Response(data)

        user: User = User.objects.get(username=info["username"])

        # check if request exists
        if not Friends.objects.filter(
            id=int(req_data["id"]), friend2=user, accepted=False
        ).exists():
            data = {"success": False, "description": "Invalid request", "data": {}}
            return Response(data)

        friend: Friends = Friends.objects.get(id=int(req_data["id"]))
        user1: User = friend.friend1
        friend.accepted = True
        friend.save(force_update=True)
        Friends.objects.filter(friend1=user, friend2=user1, accepted=False).delete()
        data = {"success": True, "description": "Request accepted", "data": {}}
        return Response(data)


class DeclineRequestView(APIView):
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

        # must be user
        if not User.objects.filter(username=info["username"]).exists():
            data = {"success": False, "description": "Not a user", "data": {}}
            return Response(data)

        user: User = User.objects.get(username=info["username"])

        # check if request exists
        if not Friends.objects.filter(
            id=int(req_data["id"]), friend2=user.id, accepted=False
        ).exists():
            data = {"success": False, "description": "Invalid request", "data": {}}
            return Response(data)

        Friends.objects.filter(id=int(req_data["id"]), accepted=False).delete()
        data = {"success": True, "description": "Request decliened", "data": {}}
        return Response(data)


class DeleteFriendView(APIView):
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

        # must be user
        if not User.objects.filter(username=info["username"]).exists():
            data = {"success": False, "description": "Not a user", "data": {}}
            return Response(data)

        user: User = User.objects.get(username=info["username"])

        # check if request exists
        if not (
            Friends.objects.filter(id=int(req_data["id"]), friend2=user.id).exists()
            or Friends.objects.filter(id=int(req_data["id"]), friend1=user.id).exists()
        ):
            data = {"success": False, "description": "Invalid request", "data": {}}
            return Response(data)

        f: Friends = Friends.objects.get(id=int(req_data["id"]))
        removed_friend: User = f.friend1
        if removed_friend.id == user.id:
            removed_friend = f.friend2
        Friends.objects.filter(id=int(req_data["id"])).delete()

        data = {
            "success": True,
            "description": "Removed friend",
            "data": {"removed_friend": removed_friend.username},
        }
        return Response(data)


class GetProfileOfFriendView(APIView):
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

        # must be user
        if not User.objects.filter(username=info["username"]).exists():
            data = {"success": False, "description": "Not a user", "data": {}}
            return Response(data)
        user1: User = User.objects.get(username=info["username"])

        # valid user
        if not User.objects.filter(username=req_data["username"]).exists():
            data = {"success": False, "description": "User does not exist", "data": {}}
            return Response(data)
        user2: User = User.objects.get(username=req_data["username"])

        # are friends
        if not (
            Friends.objects.filter(friend1=user1, friend2=user2, accepted=True).exists()
            or Friends.objects.filter(
                friend1=user2, friend2=user1, accepted=True
            ).exists()
        ):
            data = {"success": False, "description": "Not a friend", "data": {}}
            return Response(data)

        data = {
            "success": True,
            "description": "Returning profile",
            "data": FriendHandler.get_profile(user2),
        }
        return Response(data)
