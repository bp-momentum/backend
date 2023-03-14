from hashlib import sha256
from rest_framework.views import APIView
from rest_framework.response import Response

from MomentumBackend.models import SetStats
from ..settings import CONFIGURATION

from MomentumBackend.Helperclasses.handlers import ErrorHandler

class SendFeedbackView(APIView):
    def post(self, request, *args, **kwargs):
        check = ErrorHandler.check_arguments(
            [],
            request.headers,
            ["set_uuid", "values", "checksum"],
            request.data,
        )
        if not check.get("valid"):
            data = {
                "success": False,
                "description": "Missing arguments",
                "data": check.get("missing"),
            }
            return Response(data)
        
        set_uuid = request.data["set_uuid"]
        ai_psk = CONFIGURATION.get("ai_psk")

        # checksum is sha256 of set_uuid + psk
        checksum = sha256(f"{set_uuid}{ai_psk}".encode()).hexdigest()
        if checksum != request.data["checksum"]:
            data = {
                "success": False,
                "description": "Checksum is invalid",
            }
            return Response(data)
        
        SetStats.objects.filter(set_uuid=set_uuid).update(
            speed=request.data["values"]["speed"],
            accuracy=request.data["values"]["accuracy"],
            cleanliness=request.data["values"]["cleanliness"],
        )

        data = {
            "success": True,
            "description": "Feedback successfully saved",
        }
        return Response(data)