from ..Helperclasses.ai import AIInterface
from rest_framework.views import APIView
from rest_framework.response import Response
from ..Helperclasses.jwttoken import JwToken
from ..Helperclasses.handlers import ErrorHandler

class AIView(APIView):
    def post(self, request, *args, **kwargs):
        #checking if it contains all arguments
        check = ErrorHandler.check_arguments(['Session-Token'], request.headers, ['exercise', 'video'], request.data)
        if not check.get('valid'):
            data = {
                'success': False,
                'description': 'Missing arguments',
                'data': check.get('missing')
            }
            return Response(data)
        req_data = dict(request.data)
        token = JwToken.check_new_user_token(request.headers["Session-Token"])
        #check if token is valid
        if not token["valid"]:
            data = {
                'success': False,
                'description': 'Token is not valid',
                'data': {}
                }
            return Response(data)
        res = AIInterface.call_ai(req_data['exercise'], req_data['video'], token['info']['username'])
        if(res[0]):
            data = {
                    'success': True,
                    'description': 'Result available',
                    'data': {
                        'results': res[1],
                        'feedback': res[2]
                    }
            }
        else:
            data = {
                    'success': False,
                    'description': 'Result not available',
                    'data': {}
            }
        return Response(data)