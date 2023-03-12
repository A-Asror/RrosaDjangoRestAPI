from enum import Enum
from typing import AnyStr, Optional, Union

from django.contrib.postgres.indexes import BrinIndex
from django.db import models, transaction
from django.db.models.manager import Manager
from django.utils import timezone

from src.utils.exceptions import ValidationError

from .manager import CustomModelBase


class BaseModel(models.Model, metaclass=CustomModelBase):
    created_at = models.DateTimeField(editable=False, null=True, blank=True)
    updated_at = models.DateTimeField(editable=False, null=True, blank=True)
    objects = Manager()

    class Meta:
        abstract = True
        indexes = (BrinIndex(fields=("created_at", "updated_at")),)

    def save(self, update: Optional[dict] = None, update_fields: Union[list[AnyStr], tuple[AnyStr], None] = None, *args, **kwargs):
        from src.base.utils import setattr_for_save_obj

        if not self.id:
            self.created_at = timezone.localtime(timezone.now())
        self.updated_at = timezone.localtime(timezone.now())
        setattr_for_save_obj(self, update)
        update_fields = self.__check_update_fields(update, update_fields)

        return self.__save(*args, update_fields=update_fields, **kwargs)

    def __save(self, *args, update_fields: Union[list, None] = None, **kwargs):
        is_updated = kwargs.pop("is_updated", False)
        if (update_fields is not None) and len(update_fields) > 0:
            with transaction.atomic():
                super(BaseModel, self).save(*args, update_fields=update_fields, **kwargs)
        if not is_updated:
            super(BaseModel, self).save(*args, **kwargs)
        return self

    def __check_update_fields(self, update, update_fields) -> list:
        _update_fields = []
        from src.base.utils import get_list_dict_keys

        new_update_fields = get_list_dict_keys(update, self) if (update is not None) else None
        if new_update_fields is not None:
            if (update_fields is not None) and isinstance(update_fields, list):
                _update_fields = update_fields + new_update_fields
            else:
                _update_fields = new_update_fields

        attrs = [field.name for field in self._meta.fields]
        if update_fields is not None:
            for upd_field in update_fields:
                if (upd_field not in attrs) and ("_%s" % upd_field in attrs):
                    _update_fields.append("_%s" % upd_field)
                elif upd_field in attrs:
                    _update_fields.append(upd_field)
        return _update_fields

    @classmethod
    def update_fields(cls, user, **data) -> Union[tuple, list]:
        """
        Метод для перечислений доступных для изменений аттрибутов, исходя от роли пользователя.
        Метод должен возвращать список аттрибутов.
        Example: ['username', 'email', ....]
        """
        raise NotImplementedError

    def get_upload_url(self):
        """Метод получения Пути для сохранения файла."""
        raise NotImplementedError


class BaseEnum(Enum):
    @classmethod
    def get_value_by_name(cls, name: str):
        instance = getattr(cls, name, None)
        if instance is None:
            raise ValidationError(detail="%s not found 'choice name'" % name)
        return instance.value

    @classmethod
    def get_name_by_value(cls, value: Union[int, str, None]):
        try:
            return cls(value).name
        except ValueError:
            raise ValidationError(detail="%s not found 'choice value'" % value)

    @classmethod
    def get_choice(cls):
        return [(attr.value, attr.name) for attr in cls]

    @classmethod
    def get_list_values(cls):
        return [attr.value for attr in cls]

    @classmethod
    def get_list_names(cls):
        return [attr.name for attr in cls]

    @classmethod
    def get_max_value(cls):
        return max([attr.value for attr in cls])

    @classmethod
    def get_min_value(cls):
        return min([attr.value for attr in cls])
