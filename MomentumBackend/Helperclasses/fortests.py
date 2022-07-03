class Request:
    pass


class ViewSupport:
    @staticmethod
    def setup_request(header: dict, data: dict) -> Request:
        request = Request()
        request.headers = header
        request.data = data
        return request
