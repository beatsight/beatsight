from rest_framework.response import Response
from rest_framework import status

def ok(data, status=status.HTTP_200_OK):
    return Response({'status': 'ok', 'data': data, 'error': None }, status=status)

def client_error(err_msg: str, status=status.HTTP_400_BAD_REQUEST):
    return Response({'status': 'failed', 'data': None, 'error': err_msg }, status=status)

def server_error(err_msg: str, status=status.HTTP_500_INTERNAL_SERVER_ERROR):
    return Response({'status': 'failed', 'data': None, 'error': err_msg }, status=status)
