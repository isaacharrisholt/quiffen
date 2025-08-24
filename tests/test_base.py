# pylint: disable=too-few-public-methods,protected-access,abstract-method


from quiffen.core.base import BaseModel, Field


def test_create_field():
    """Test creating a field"""
    field = Field(line_code="T", attr="test", type=str)
    assert field.line_code == "T"
    assert field.attr == "test"
    assert field.type is str


def test_sorting_fields():
    """Test sorting fields by line code"""
    field1 = Field(line_code="A", attr="a", type=str)
    field2 = Field(line_code="B", attr="b", type=str)
    field3 = Field(line_code="AA", attr="aa", type=str)

    assert sorted([field1, field2, field3]) == [field1, field3, field2]


def test_base_model_allows_extra_fields():
    """Test that the BaseModel allows extra fields"""

    class TestModel(BaseModel):
        @classmethod
        def from_list(cls, lst: list[str]) -> None:
            pass

    test_model = TestModel(test="test")
    assert test_model.test == "test"


def test_add_custom_field():
    """Test adding a custom field to a class"""

    class TestModel(BaseModel):
        pass

    TestModel.add_custom_field("T", "test", str)
    assert TestModel._get_custom_fields() == [
        Field(line_code="T", attr="test", type=str),
    ]


def test_overwrite_custom_field():
    """Test overwriting a custom field in a class"""

    class TestModel(BaseModel):
        pass

    TestModel.add_custom_field("T", "test", str)
    TestModel.add_custom_field("T", "test2", int)
    assert TestModel._get_custom_fields() == [
        Field(line_code="T", attr="test2", type=int),
    ]


def test_custom_fields_are_not_shared():
    """Test that custom fields are not shared between classes"""

    class TestModel1(BaseModel):
        pass

    class TestModel2(BaseModel):
        pass

    TestModel1.add_custom_field("T", "test", str)
    assert TestModel1._get_custom_fields() == [
        Field(line_code="T", attr="test", type=str),
    ]
    assert not TestModel2._get_custom_fields()


def test_custom_fields_are_inherited():
    """Test that custom fields are inherited by subclasses"""

    class TestModel1(BaseModel):
        pass

    class TestModel2(TestModel1):
        pass

    TestModel1.add_custom_field("T", "test", str)
    assert TestModel1._get_custom_fields() == [
        Field(line_code="T", attr="test", type=str),
    ]
    assert TestModel2._get_custom_fields() == [
        Field(line_code="T", attr="test", type=str),
    ]
