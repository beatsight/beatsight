from rest_framework.views import exception_handler
from django.http import Http404

def custom_exception_handler(exc, context):
    # Call the default exception handler first to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the custom error response.
    if isinstance(exc, Http404):
        custom_response = {'status': 'failed', 'data': None, 'error': 'Resource not found' }
    else:
        custom_response = {'status': 'failed', 'data': None, 'error': 'Internal Server Error' }

    if response is not None:
        response.data = custom_response

    return response
