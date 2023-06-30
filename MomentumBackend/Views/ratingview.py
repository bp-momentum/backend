from hashlib import sha256

from django.http import JsonResponse
from MomentumBackend.helper.utils import get_request_data

from MomentumBackend.models import SetStats
from ..settings import CONFIGURATION

from ..helper.handlers import ErrorHandler


def rate(request):
    data = get_request_data(request)

    check = ErrorHandler.check_arguments(
        ["set_uuid", "values", "checksum"],
        data,
    )
    if not check.get("valid"):
        return check.get("response")

    set_uuid = data["set_uuid"]
    ai_psk = CONFIGURATION.get("ai_psk")

    # checksum is sha256 of set_uuid + psk
    checksum = sha256(f"{set_uuid}{ai_psk}".encode()).hexdigest()
    if checksum != data["checksum"]:
        return JsonResponse({
            "success": False,
            "description": "Checksum is invalid",
        })

    SetStats.objects.filter(set_uuid=set_uuid).update(
        speed=data["values"]["speed"],
        accuracy=data["values"]["accuracy"],
        cleanliness=data["values"]["cleanliness"],
    )

    return JsonResponse({
        "success": True,
        "description": "Feedback successfully saved",
    })
