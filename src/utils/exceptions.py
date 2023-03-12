from rest_framework.exceptions import APIException


class AuthenticationFailed(APIException):
    status_code = 401
    default_detail = 'Unauthorized.'


class PermissionFailed(APIException):
    status_code = 403
    default_detail = 'Permission denied.'


class ValidationError(APIException):
    status_code = 400
    default_detail = 'Bad Request.'
