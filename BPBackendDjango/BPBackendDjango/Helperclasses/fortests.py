class Request():
    pass

class ViewSupport():

    @staticmethod
    def setup_request(header, data):
        request = Request()
        request.headers = header
        request.data = data
        return request