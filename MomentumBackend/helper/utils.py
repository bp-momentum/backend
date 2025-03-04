import json
from django.http import JsonResponse

MIN_USERNAME_LENGTH = 3
ALLOWED = "1234567890qwertzuiopasdfghjklyxcvbnmQWERTZUIOPASDFGHJKLYXCVBNM _-"


def validate_username(name: str) -> bool:
    return (all(c in ALLOWED for c in name) and len(name) >= MIN_USERNAME_LENGTH and not str(name).startswith(" "))


def restrict_roles_403(roles: list):
    """
    Decorator for views that checks whether a user has a particular role
    enabled, returning a 403 if necessary.
    """
    def decorator(view_func):
        def _wrapper_view(request, *args, **kwargs):
            if request.user.account.role in roles:
                return view_func(request, *args, **kwargs)
            response = JsonResponse({"success": False, "data": {}})
            response.status_code = 403
            return response
        return _wrapper_view
    return decorator


def login_required_401(view_func):
    def _wrapper_view(request, *args, **kwargs):
        if True: # request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        response = JsonResponse({"success": False, "data": {}})
        response.status_code = 401
        return response
    return _wrapper_view


def get_request_data(request):
    if request.method == "GET":
        return request.GET
    elif request.POST:
        return request.POST
    else:
        return json.loads(request.body)
