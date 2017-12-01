from graphene import Enum

from sqlalchemy.types import Enum as SQLAlchemyEnumType

from .utils import to_type_name


class Registry(object):

    def __init__(self):
        self._registry = {}
        self._registry_composites = {}
        self._registry_enums = {}

    def register(self, cls):
        from .types import SQLAlchemyObjectType
        assert issubclass(cls, SQLAlchemyObjectType), (
            'Only classes of type SQLAlchemyObjectType can be registered, '
            'received "{}"'
        ).format(cls.__name__)
        assert cls._meta.registry == self, 'Registry for a Model have to match.'
        # assert self.get_type_for_model(cls._meta.model) in [None, cls], (
        #     'SQLAlchemy model "{}" already associated with '
        #     'another type "{}".'
        # ).format(cls._meta.model, self._registry[cls._meta.model])
        self._registry[cls._meta.model] = cls

    def get_type_for_model(self, model):
        return self._registry.get(model)

    def register_composite_converter(self, composite, converter):
        self._registry_composites[composite] = converter

    def get_converter_for_composite(self, composite):
        return self._registry_composites.get(composite)

    def get_type_for_enum(self, sql_type):
        assert isinstance(sql_type, SQLAlchemyEnumType), (
            'Only sqlalchemy.Enum objects can be registered as enum, '
            'received "{}"'
        ).format(sql_type)
        if sql_type.enum_class:
            name = sql_type.enum_class.__name__
            items = [(key.upper(), value.value)
                     for key, value in sql_type.enum_class.__members__.items()]
        else:
            name = to_type_name(sql_type.name)
            if not name:
                name = 'Enum{}'.format(len(self._registry_enums) + 1)
            items = [(key.upper(), key) for key in sql_type.enums]
        if name:
            gql_type = self._registry_enums.get(name)
            if gql_type:
                if dict(items) != {
                        key: value.value for key, value
                        in gql_type._meta.enum.__members__.items()}:
                    raise TypeError(
                        'Different enums with the same name {}'.format(name))
        else:
            name = 'Enum{}'.format(len(self._registry_enums) + 1)
            gql_type = None
        if not gql_type:
            gql_type = Enum(name, items)
            self._registry_enums[name] = gql_type
        return gql_type


registry = None


def get_global_registry():
    global registry
    if not registry:
        registry = Registry()
    return registry


def reset_global_registry():
    global registry
    registry = None
