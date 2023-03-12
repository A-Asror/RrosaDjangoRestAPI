import datetime as dt
from typing import Any, Union

from django.conf import settings
from django.db.models import Model, Q, QuerySet

# from src.base.file_uploader import FileUploader, check_prefix_image, check_size_image
from src.base.models import BaseModel
from src.utils.exceptions import ValidationError


def get_list_dict_keys(payload: dict, obj) -> list:
    return [attr for attr in list(payload.keys()) if not isinstance(getattr(obj, attr), Model)]


# def create_images(images: list[UploadedFile], url: str, db_kwargs: Union[dict, str]):  # db_files: dict
#     """Функция принимает список Изображений для сохранения."""
#     image_str = False
#     for image in images:
#         check_size_image(image)  # validation size
#         check_prefix_image(image)  # validation prefix
#     if isinstance(db_kwargs, str):
#         image_str = True
#         db_kwargs = {}
#     img = FileUploader(images, url, db_kwargs)
#     if image_str:
#         return img.create_images().get("file_1")
#     return img.create_images()


def update(user, obj: BaseModel, payload: dict) -> BaseModel:
    """
    Функция для обновления любого экземпляра models.Model, и любого вложенности Объектов.
    Проверка наличия полей в Объекте, проверяется с помощью встроенного метода python: "hasattr"
    Для изменений полей используется встроенный метод python: "setattr"
    Для изменений вложенных объектов как OneToOneField или ForeignKey используется встроенный метода python: "getattr",
        затем заново вызывается этот же метод: "update" и передается:
        вложенный OneToOneField или ForeignKey Объект. для просмотра этой части смотрите: 61-62 строки
    Argument:
    ----------
    :arg user: Это экземпляр UserModel, и этот параметр нужен для того чтоб проверить; Может ли этот пользователь изменить
        аттрибуты, переданного Объекта для изменения, это проверяется с помощью метода update_fields у переданного
        объекта
    :arg obj: Это Объект который будет изменен
    :arg payload: Это словарь или Экземпляр схемы BaseModel из pydantic(а), в этом параметре передается аттрибуты и их
       значения для изменения Объекта(obj)
    """
    return _update(user, obj, payload)


def _update(user, obj: BaseModel, payload: dict) -> BaseModel:
    payload: dict = __standardization_update_attrs(payload)
    update_fields = obj.update_fields(user, **payload)
    for attr, new_value in payload.items():
        obj_attrs: list = get_list_model_attrs_name(obj)
        # print(hasattr(obj, attr) and (not isinstance(new_value, dict) or (attr in obj_attrs)))
        if hasattr(obj, attr) and not isinstance(new_value, dict) and (attr not in update_fields):
            raise ValidationError(code=400, detail="permission denied")
        if hasattr(obj, attr) and (not isinstance(new_value, dict) or (attr in obj_attrs)):
            setattr(obj, attr, new_value)
        elif hasattr(obj, attr) and isinstance(new_value, dict) and (attr not in obj_attrs):
            _update(user, getattr(obj, attr), new_value)
    _update_fields = get_list_dict_keys(payload, obj)
    obj.save(update_fields=_update_fields, is_updated=True)
    return obj


def __standardization_update_attrs(payload: dict) -> dict:
    """Стандартизация объектов для обновления.
    Функция перепишет все связанные поля написанные с двойным нижним подчеркиванием и точечным путем до объекта
    Example:
        {fk_attr__attr: value} to {fk_attr: {attr: value}}
        or
        {fk_attr.attr: value} to {fk_attr: {attr: value}}
    """
    payload_iter = payload.copy()
    for attr, value in payload_iter.items():
        fk_attrs: list = []
        fk_attrs_underscore: list = attr.split("__")
        fk_attrs_point: list = attr.split(".")
        if len(fk_attrs_underscore) > 1:
            [fk_attrs.append(_attr) for _attr in fk_attrs_underscore]
        elif len(fk_attrs_point) > 1:
            [fk_attrs.append(_attr) for _attr in fk_attrs_underscore]
        if fk_attrs:
            __standardization_update_attrs_service(fk_attrs, attr, value, payload)
    return payload


def __standardization_update_attrs_service(fk_attrs: list, attr: str, value: Any, payload: dict) -> dict:
    _data = dict()
    if len(fk_attrs) > 1:
        for fk_attr in fk_attrs[::-1]:
            if not _data:
                _data[fk_attr] = value
            else:
                _data = {fk_attr: _data}
    payload.update(_data)
    del payload[attr]
    return payload


def remove_null_from_Q_object(q_data):
    """
    Задача этой функции удалить все Q объекты.
    Где значение атрибута Q, равна на None Q(attr=None)
    result: если все атрибуты Q равны на None Q(attr=None), то вернет пустой tuple и False
     иначе если хоть 1 атрибут Q не равно на None, то он вернет объект Q и True
     True и False нужен узнать чтоб для фильтрации надо-ли фильтровать специально под Q объектов
    """
    return _remove_null_from_Q_object(q_data)


def _remove_null_from_Q_object(q_data):
    for num in range(len(q_data) - 1, -1, -1):
        if type(q_data.children[num]) is tuple:
            if isinstance(q_data.children[num][1], None):
                del q_data.children[num]
        elif type(q_data.children[num]) is Q:
            remove_null_from_Q_object(q_data.children[num])
    if len(q_data) == 0:
        return tuple(), False
    return q_data, True


def paginator(queryset: QuerySet, page: int, page_size: int = 15) -> QuerySet:
    end = page * page_size
    start = end - page_size
    return queryset[start:end]


def setattr_for_save_obj(obj, update: Union[dict, None]):
    """
    Для автоматизации обновлений.
    Argument:
    ----------
    obj: Object
        obj - Это один из дочериных классов src.models.BaseModel(a)
        Используется при обновлении аттрибутов этого объекта(obj), который был передан в параметре: kwargs
    data: update
        data - Это dict или None
        Используется при обновлении аттрибутов Объекта(obj)
        Если дата None то метод вернет None и не обновит никаких аттрибутов
    Этот метод срабатывает при вызове метода .save() у всех дочериных классах src.models.BaseModel(a)
    Метод упрощает обновлений аттрибутов, пример:
        Обычно чтоб изменить аттрибут объекта пишется:
        obj.attr = new_value
        obj.attr2 = new_value2
        obj.attr3 = new_value3
        ....
        obj.save()
        Чтобы упрощать этот процесс и уменьшить кол-во строк, теперь можно:
        obj.save(update={"attr": "new_value", "attr2": new_value, "attr3": new_value, ....})
    """
    return _setattr_for_save_obj(obj, update)


def _setattr_for_save_obj(obj, update: Union[dict, None]):
    data = update

    if data is None:
        return

    for attr, value in data.items():
        if hasattr(obj, attr):
            setattr(obj, attr, value)


def get_list_model_attrs_name(cls) -> list:
    if isinstance(cls, Model):
        return [field.name for field in cls._meta.fields]
    return []


def reformat_file(files: Union[dict, str, None]):
    data = dict()
    domain = settings.DOMAIN_BACK_END
    if files is None:
        return files
    elif isinstance(files, str):
        return domain + files
    for key, value in files.items():
        data[key] = domain + value if isinstance(value, str) else None
    return data


def normalize_date_out(date: Union[dt.date, None]):
    if date is None:
        return None
    return date.strftime("%d/%m/%Y")


def normalize_date_in(date: Union[dt.date, None]):
    if date is None:
        return None
    return dt.datetime.strptime(date, "%d/%m/%Y").date()


def set_data(value: Union[str, None], attr_name: str, data: dict) -> None:
    if value is not None:
        data[attr_name] = value
    return