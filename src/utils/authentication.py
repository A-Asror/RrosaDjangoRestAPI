from typing import Union
from secrets import compare_digest as compare_secret_data

import jwt

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed

# from base.cache import AuthUserCache

from src.users.models import UserModel


ERROR_PAYLOAD = 'Invalid payload. User with *id not found.'


def decode_token(token: str) -> Union[dict, AuthenticationFailed]:
    try:
        decode_data = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        return decode_data
    except Exception:
        msg = _('Invalid token.')
        raise AuthenticationFailed(msg)


def chek_token_life(decode_data: dict) -> bool:
    exp = decode_data['exp']
    if int(timezone.localtime(timezone.now()).timestamp()) < exp:
        return True
    return False


def validation_user(user):
    if user is None:
        msg = _(ERROR_PAYLOAD)
        raise AuthenticationFailed(msg)
    elif not user.is_active:
        msg = _('Invalid user. the user is blocked.')
        raise AuthenticationFailed(msg)
    elif isinstance(user, AbstractBaseUser) is False:
        msg = _('Invalid user')
        raise AuthenticationFailed(msg)
    try:
        user.jwt
    except UserModel.jwt.RelatedObjectDoesNotExist:  # RelatedObjectDoesNotExist
        msg = _('Invalid token. please log in')
        raise AuthenticationFailed(msg)


class JWTAuthentication(authentication.BaseAuthentication):
    authentication_header_prefix = 'bearer'
    refresh = False
    request = None
    token = None

    def authenticate(self, request):
        request.user = None
        self.request = request
        auth_header = authentication.get_authorization_header(request).split()

        if 'login/' in request.path or 'register/' in request.path:
            return None

        if len(auth_header) == 0:
            return None
        elif len(auth_header) == 1:
            msg = _('Invalid token header. No credentials provided.')
            raise AuthenticationFailed(msg)
        elif len(auth_header) > 2:
            msg = _('Invalid token header. Token string should not contain spaces.')
            raise AuthenticationFailed(msg)

        prefix = auth_header[0].decode('utf-8')

        if not auth_header or prefix.lower() != self.authentication_header_prefix:
            return None

        self.token = auth_header[1].decode('utf-8')
        # user = self.get_user  # get user from cache

        # if user and isinstance(user, AbstractBaseUser):
        #     return user, True

        data = decode_token(self.token)
        if data and chek_token_life(data):
            return self._authenticate_credentials(data)
        return None

    def _authenticate_credentials(self, payload):
        try:
            user = UserModel.objects.select_related('jwt', ).get(pk=payload['id'])
        except Exception:
            msg = _(ERROR_PAYLOAD)
            raise AuthenticationFailed(msg)

        validation_user(user)
        # if self.token != user.jwt.access or self.request.COOKIES.get('_at', '!@$%^') != user.jwt.refresh:
        if compare_secret_data(self.token, user.jwt.access):
            msg = _('Invalid access and refresh tokens. No credentials provided.')
            raise AuthenticationFailed(msg)
        self.request.user = user
        return self.request.user, True


class RefreshJWTAuthentication(JWTAuthentication):

    def _authenticate_credentials(self, payload):

        try:
            user = UserModel.objects.select_related('jwt', ).get(pk=payload['id'])
        except UserModel.meta.DoesNotExist:
            msg = _(ERROR_PAYLOAD)
            raise AuthenticationFailed(msg)

        validation_user(user)

        if compare_secret_data(self.token, user.jwt.refresh) or self.request.COOKIES.get('_at', '!@$%^') != user.jwt.refresh:
            msg = _('Invalid access and refresh tokens. No credentials provided.')
            raise AuthenticationFailed(msg)
        self.request.user = user
        return self.request.user, True
