from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # Custom handling for specific error types
    if response is not None:
        if response.status_code == 404:
            response.data = {"detail": "The requested resource was not found."}
        elif response.status_code == 400:
            response.data = {"detail": "Invalid request. Please check the data you sent."}
        elif response.status_code == 500:
            response.data = {"detail": "Internal server error. Please try again later."}
    else:
        # Unhandled error
        response = Response({"detail": "Unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response
