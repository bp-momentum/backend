from django.http import JsonResponse


class ErrorHandler:
    @staticmethod
    def check_arguments(expected_data, data) -> dict:
        missing_data = []
        missing = False

        if type(expected_data) == list:
            for d in expected_data:
                if data.get(d) == None:
                    missing_data.append(d)
                    missing = True
        elif type(expected_data) == dict:
            # dict: {<name>: {name: <name>, required: <bool>}}
            for d in expected_data:
                if expected_data[d]["required"] and data.get(d) == None:
                    missing_data.append(d)
                    missing = True

        return {
            "valid": not missing,
            "response": JsonResponse({
                "success": False,
                "description": "Missing arguments",
                "data": missing_data,
            })
        }
