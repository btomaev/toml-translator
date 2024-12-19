import pytest
from app import verify_name, verify_expr, translate, TranslationError

def test_verify_name():
    assert verify_name("valid_name") is not None
    assert verify_name("_underscore") is not None
    assert verify_name("123invalid") is None
    assert verify_name("invalid-name") is None
    assert verify_name("") is None

def test_verify_expr():
    assert verify_expr("^(+ var 5)") is not None
    assert verify_expr("^(- var 3.2)") is not None
    assert verify_expr("^(sqrt var)") is not None
    assert verify_expr("invalid_expr") is None

def test_translate_simple_dict():
    obj = {"a": 10, "b": {"c": 20, "d": 30}}
    result = translate(obj, root=True)
    assert "const a = 10;" in result
    assert "const b = {" in result
    assert "    c : 20," in result
    assert "    d : 30" in result

def test_translate_with_expression():
    obj = {"a": 10, "b": "^(+ a 5)"}
    result = translate(obj, root=True)
    assert "const a = 10;" in result
    assert "const b = 15;" in result

def test_translate_invalid_expression():
    obj = {"a": 10, "b": "^(+ c 5)"}
    with pytest.raises(NameError, match="const c not found"):
        translate(obj, root=True)

def test_translate_invalid_key_name():
    obj = {"invalid-key": 10}
    with pytest.raises(NameError, match=r'Names should be \[_a-zA-Z\]\[_a-zA-Z0-9\]\* but "invalid-key" found'):
        translate(obj, root=True)

def test_translate_unknown_type():
    obj = {"a": object()}
    with pytest.raises(TranslationError, match="Unknown type <class 'object'> at line: .*"):
        translate(obj, root=True)

def test_translate_list():
    obj = {"a": [10]}
    result = translate(obj, root=True)
    assert "const a = 10;" in result
