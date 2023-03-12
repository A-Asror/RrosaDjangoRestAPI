
import copy
from itertools import chain

from django.apps import apps
from django.core.exceptions import (
    FieldDoesNotExist,
    FieldError,
    MultipleObjectsReturned,
    ObjectDoesNotExist,
)
from django.db.models.base import (
    ModelBase,
    _has_contribute_to_class,
    subclass_exception,
)
from django.db.models.deletion import CASCADE
from django.db.models.fields.related import ForeignKey, OneToOneField, resolve_relation
from django.db.models.options import Options  # Надо изменить
from django.db.models.utils import make_model_tuple


class MyOptions(Options):
    def get_field(self, field_name):
        list_fields = []
        for field in self.model._meta.fields:
            if isinstance(field, (ForeignKey, OneToOneField)):
                list_fields.extend([field.name, "%s_id" % field.name])
            else:
                list_fields.append(field.name)
        if (field_name not in list_fields) and ("_%s" % field_name in list_fields):
            field_name = "_%s" % field_name
        return super(MyOptions, self).get_field(field_name)


class CustomModelBase(ModelBase):
    def __new__(cls, name, bases, attrs, **kwargs):
        super_new = type.__new__

        parents = [b for b in bases if isinstance(b, ModelBase)]
        if not parents:
            return super_new(cls, name, bases, attrs)

        module = attrs.pop("__module__")
        new_attrs = {"__module__": module}
        classcell = attrs.pop("__classcell__", None)
        if classcell is not None:
            new_attrs["__classcell__"] = classcell
        attr_meta = attrs.pop("Meta", None)

        contributable_attrs = {}
        for obj_name, obj in attrs.items():
            if _has_contribute_to_class(obj):
                contributable_attrs[obj_name] = obj
            else:
                new_attrs[obj_name] = obj
        new_class = super_new(cls, name, bases, new_attrs, **kwargs)

        abstract = getattr(attr_meta, "abstract", False)
        meta = attr_meta or getattr(new_class, "Meta", None)
        base_meta = getattr(new_class, "_meta", None)

        app_label = None

        app_config = apps.get_containing_app_config(module)

        if getattr(meta, "app_label", None) is None:
            if app_config is None:
                if not abstract:
                    raise RuntimeError(
                        "Model class %s.%s doesn't declare an explicit " "app_label and isn't in an application in " "INSTALLED_APPS." % (module, name)
                    )

            else:
                app_label = app_config.label

        new_class.add_to_class("_meta", MyOptions(meta, app_label))
        if not abstract:
            new_class.add_to_class(
                "DoesNotExist",
                subclass_exception(
                    "DoesNotExist",
                    tuple(x.DoesNotExist for x in parents if hasattr(x, "_meta") and not x._meta.abstract) or (ObjectDoesNotExist,),
                    module,
                    attached_to=new_class,
                ),
            )
            new_class.add_to_class(
                "MultipleObjectsReturned",
                subclass_exception(
                    "MultipleObjectsReturned",
                    tuple(x.MultipleObjectsReturned for x in parents if hasattr(x, "_meta") and not x._meta.abstract) or (MultipleObjectsReturned,),
                    module,
                    attached_to=new_class,
                ),
            )
            if base_meta and not base_meta.abstract:
                if not hasattr(meta, "ordering"):
                    new_class._meta.ordering = base_meta.ordering
                if not hasattr(meta, "get_latest_by"):
                    new_class._meta.get_latest_by = base_meta.get_latest_by

        is_proxy = new_class._meta.proxy

        if is_proxy and base_meta and base_meta.swapped:
            raise TypeError("%s cannot proxy the swapped model '%s'." % (name, base_meta.swapped))

        for obj_name, obj in contributable_attrs.items():
            new_class.add_to_class(obj_name, obj)

        new_fields = chain(new_class._meta.local_fields, new_class._meta.local_many_to_many, new_class._meta.private_fields)
        field_names = {f.name for f in new_fields}

        if is_proxy:
            base = None
            for parent in [kls for kls in parents if hasattr(kls, "_meta")]:
                if parent._meta.abstract:
                    if parent._meta.fields:
                        raise TypeError("Abstract base class containing model fields not " "permitted for proxy model '%s'." % name)
                    else:
                        continue
                if base is None:
                    base = parent
                elif parent._meta.concrete_model is not base._meta.concrete_model:
                    raise TypeError("Proxy model '%s' has more than one non-abstract model base class." % name)
            if base is None:
                raise TypeError("Proxy model '%s' has no non-abstract model base class." % name)
            new_class._meta.setup_proxy(base)
            new_class._meta.concrete_model = base._meta.concrete_model
        else:
            new_class._meta.concrete_model = new_class

        parent_links = {}
        for base in reversed([new_class] + parents):
            if not hasattr(base, "_meta"):
                continue
            if base != new_class and not base._meta.abstract:
                continue
            for field in base._meta.local_fields:
                if isinstance(field, OneToOneField) and field.remote_field.parent_link:
                    related = resolve_relation(new_class, field.remote_field.model)
                    parent_links[make_model_tuple(related)] = field

        inherited_attributes = set()
        for base in new_class.mro():
            if base not in parents or not hasattr(base, "_meta"):
                inherited_attributes.update(base.__dict__)
                continue

            parent_fields = base._meta.local_fields + base._meta.local_many_to_many
            if not base._meta.abstract:
                for field in parent_fields:
                    if field.name in field_names:
                        raise FieldError(
                            "Local field %r in class %r clashes with field of "
                            "the same name from base class %r."
                            % (
                                field.name,
                                name,
                                base.__name__,
                            )
                        )
                    else:
                        inherited_attributes.add(field.name)

                base = base._meta.concrete_model
                base_key = make_model_tuple(base)
                if base_key in parent_links:
                    field = parent_links[base_key]
                elif not is_proxy:
                    attr_name = "%s_ptr" % base._meta.model_name
                    field = OneToOneField(
                        base,
                        on_delete=CASCADE,
                        name=attr_name,
                        auto_created=True,
                        parent_link=True,
                    )

                    if attr_name in field_names:
                        raise FieldError(
                            "Auto-generated field '%s' in class %r for "
                            "parent_link to base class %r clashes with "
                            "declared field of the same name."
                            % (
                                attr_name,
                                name,
                                base.__name__,
                            )
                        )

                    if not hasattr(new_class, attr_name):
                        new_class.add_to_class(attr_name, field)
                else:
                    field = None
                new_class._meta.parents[base] = field
            else:
                base_parents = base._meta.parents.copy()

                for field in parent_fields:
                    if field.name not in field_names and field.name not in new_class.__dict__ and field.name not in inherited_attributes:
                        new_field = copy.deepcopy(field)
                        new_class.add_to_class(field.name, new_field)

                        if field.one_to_one:
                            for parent, parent_link in base_parents.items():
                                if field == parent_link:
                                    base_parents[parent] = new_field

                new_class._meta.parents.update(base_parents)

            for field in base._meta.private_fields:
                if field.name in field_names:
                    if not base._meta.abstract:
                        raise FieldError(
                            "Local field %r in class %r clashes with field of "
                            "the same name from base class %r."
                            % (
                                field.name,
                                name,
                                base.__name__,
                            )
                        )
                else:
                    field = copy.deepcopy(field)
                    if not base._meta.abstract:
                        field.mti_inherited = True
                    new_class.add_to_class(field.name, field)

        new_class._meta.indexes = [copy.deepcopy(idx) for idx in new_class._meta.indexes]

        if abstract:
            attr_meta.abstract = False
            new_class.Meta = attr_meta
            return new_class

        new_class._prepare()
        new_class._meta.apps.register_model(new_class._meta.app_label, new_class)
        return new_class
