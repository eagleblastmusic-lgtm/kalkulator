from decimal import Decimal

import pytest

from calculator import CalculatorEngine, calculate, format_number


@pytest.mark.parametrize("left,op,right,expected", [
    ("2", "+", "3", "5"), ("8", "-", "3", "5"),
    ("4", "*", "2.5", "10"), ("9", "/", "4", "2.25"),
])
def test_calculate(left, op, right, expected):
    assert calculate(Decimal(left), op, Decimal(right)) == Decimal(expected)


def test_invalid_operations():
    with pytest.raises(ZeroDivisionError):
        calculate(Decimal("1"), "/", Decimal("0"))
    with pytest.raises(ValueError, match="Unsupported"):
        calculate(Decimal("1"), "^", Decimal("2"))


@pytest.mark.parametrize("value,expected", [
    ("5.000", "5"), ("0.1250", "0.125"), ("-0", "0"),
])
def test_format_number(value, expected):
    assert format_number(Decimal(value)) == expected


def test_input_and_decimal():
    engine = CalculatorEngine()
    assert engine.digit("1") == "1"
    assert engine.digit("2") == "12"
    assert engine.decimal() == "12."
    assert engine.decimal() == "12."
    assert engine.digit("5") == "12.5"


def test_chained_operations():
    engine = CalculatorEngine()
    engine.digit("8")
    engine.choose("+")
    engine.digit("2")
    engine.choose("*")
    engine.digit("3")
    assert engine.equals() == "30"


def test_clear_backspace_and_sign():
    engine = CalculatorEngine(display="12")
    assert engine.backspace() == "1"
    assert engine.sign() == "-1"
    assert engine.sign() == "1"
    assert engine.clear() == "0"
    assert engine.accumulator is None


def test_percent():
    assert CalculatorEngine(display="25").percent() == "0.25"


def test_division_by_zero_recovers_on_next_digit():
    engine = CalculatorEngine(display="9")
    engine.choose("/")
    engine.digit("0")
    assert engine.equals() == "Error"
    assert engine.error is True
    assert engine.digit("7") == "7"
    assert engine.error is False


def test_noop_equals_and_invalid_digit():
    assert CalculatorEngine(display="12").equals() == "12"
    with pytest.raises(ValueError, match="digit"):
        CalculatorEngine().digit("x")
