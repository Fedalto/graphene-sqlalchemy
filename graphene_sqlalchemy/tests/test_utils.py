from graphene import ObjectType, Schema, String

from ..utils import get_session, to_type_name


def test_get_session():
    session = 'My SQLAlchemy session'

    class Query(ObjectType):
        x = String()

        def resolve_x(self, info):
            return get_session(info.context)

    query = '''
        query ReporterQuery {
            x
        }
    '''

    schema = Schema(query=Query)
    result = schema.execute(query, context_value={'session': session})
    assert not result.errors
    assert result.data['x'] == session


def test_get_enum_name():
    assert to_type_name('make_camel_case') == 'MakeCamelCase'
    assert to_type_name('AlreadyCamelCase') == 'AlreadyCamelCase'
