from typing import Any, List, Optional, Tuple, TypeVar, Union

from django.db import models
from django.http import Http404

from src.utils.exceptions import ValidationError

Model = TypeVar("Model", bound=models.Model)


def get_object_or_404(
    model: Union[Model, Any],
    select_related: Optional[Union[list, tuple]] = (None,),
    prefetch_related: Optional[Union[list, tuple]] = (None,),
    annotate: Optional[dict] = None,
    only: Optional[Union[list, tuple, None]] = None,
    exclude_fields: Optional[Union[list, tuple, None]] = None,
    raise_exception: bool = True,
    raise_error_text: Optional[str] = None,
    *args,
    **kwargs,
) -> Union[Model, None]:

    qs = (
        model.objects.all()
        .select_related(*select_related)
        .prefetch_related(*prefetch_related)
        .annotate(**annotate if annotate is not None else {})
        .only(*only if only is not None else ())
        .defer(*exclude_fields if exclude_fields is not None else ())
    )
    try:
        return qs.get(*args, **kwargs)
    except model.DoesNotExist:
        if not raise_exception:
            return None
        elif raise_exception and (raise_error_text is not None):
            raise Http404(raise_error_text)
        raise Http404("No %s matches the given query." % model._meta.object_name)


def get_or_create(
    model: Union[Model, Any],
    select_related: Optional[Union[list, tuple]] = (None,),
    prefetch_related: Optional[Union[list, tuple]] = (None,),
    annotate: Optional[dict] = None,
    only_fields: Optional[Union[list, tuple, None]] = None,
    exclude_fields: Optional[Union[list, tuple, None]] = None,
    *args,
    **kwargs,
) -> Model:

    qs = (
        model.objects.all()
        .select_related(*select_related)
        .prefetch_related(*prefetch_related)
        .annotate(**annotate if annotate is not None else {})
        .only(*only_fields if only_fields is not None else ())
        .defer(*exclude_fields if exclude_fields is not None else ())
    )
    return qs.get_or_create(*args, **kwargs)


def exists_model_from_data(model: Model, *args, raise_exception: bool = False, raise_error_text: Optional[str] = None, **kwargs) -> bool:
    """Если raise_exception=True то выдаст ошибку, это похож как serializer.is_valid(raise_exception)."""
    if not issubclass(model, models.Model):
        raise ValidationError(detail="%s is not a subclass models.Model" % model.__class__.__name__)
    exist = model.objects.filter(*args, **kwargs).exists()
    if raise_exception and (not exist) and (raise_error_text is not None):
        raise Http404(raise_error_text)
    if raise_exception and (not exist):
        raise Http404("No %s matches the given query." % model._meta.object_name)
    return exist


def base_sql_request(
    model,
    filter_data: Optional[dict] = None,
    q_filter_data: Optional[Union[tuple, list]] = models.Q(),
    execute_data: Optional[dict] = None,
    q_execute_data: Optional[Union[tuple, list]] = models.Q(),
    select_related: Optional[Union[list, tuple]] = (None,),
    prefetch_related: Optional[Union[list, tuple]] = (None,),
    only: Optional[Union[list, tuple]] = None,
    defer: Optional[Union[list, tuple]] = None,
    annotate: Optional[dict] = None,
    order_by: Optional[Union[list, tuple]] = None,
) -> models.QuerySet[Model]:
    qs = (
        model.objects.all()
        .select_related(*select_related)
        .prefetch_related(*prefetch_related)
        .filter(q_filter_data, **filter_data if filter_data is not None else {})
        .exclude(q_execute_data, **execute_data if execute_data is not None else {})
        .annotate(**annotate if annotate is not None else {})
        .only(*only if only is not None else ())
        .defer(*defer if defer is not None else ())
        .order_by(*order_by if order_by is not None else ())
    )

    return qs
