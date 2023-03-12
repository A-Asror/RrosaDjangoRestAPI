from django.db.models import Q, QuerySet
from rest_framework import serializers, status

from src.utils import exceptions as exc
from src.base.serializers import BaseSerializer, BaseModelSerializer

from .models import UserModel


class RegistrationSerializer(BaseModelSerializer):
    username: str = serializers.CharField(max_length=128, min_length=2, required=True)
    email: str = serializers.EmailField(max_length=50, min_length=4, required=True)
    fullname: str = serializers.CharField(max_length=128, min_length=4, required=True)
    # dob: str = serializers.DateField(required=True)
    password: str = serializers.CharField(max_length=128, min_length=8, write_only=True)
    confirm_password: str = serializers.CharField(max_length=128, min_length=8, write_only=True)

    class Meta:
        model = UserModel
        fields = ['password', 'confirm_password', 'username', 'email', 'fullname']

    def is_valid(self, *, raise_exception=False) -> bool:
        validate: bool = super(RegistrationSerializer, self).is_valid(raise_exception=raise_exception)
        if self.validated_data["password"] != self.validated_data["confirm_password"]:
            raise exc.ValidationError(detail="passwords do not match", code=status.HTTP_400_BAD_REQUEST)
        elif UserModel.objects.filter(Q(username=self.validated_data["username"]) | Q(email=self.validated_data["email"])).exists():
            raise exc.ValidationError(detail="A user with the same email or username already exists", code=status.HTTP_401_UNAUTHORIZED)
        return validate

    def create(self, validated_data: dict) -> UserModel:
        del validated_data["confirm_password"]
        password = validated_data.pop("password")
        user = UserModel(**validated_data)
        user.set_password(password)
        return user.save()


class LoginSerializer(BaseSerializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, min_length=8)

    def login(self) -> UserModel:
        user: QuerySet[UserModel] = UserModel.objects.filter(email=self.validated_data["email"])
        if len(user) != 1:
            raise exc.ValidationError(detail="User not found !", code=status.HTTP_404_NOT_FOUND)
        elif not user[0].check_password(self.validated_data["password"]):
            raise exc.ValidationError(detail="Password not correct !", code=status.HTTP_401_UNAUTHORIZED)
        return user[0]
