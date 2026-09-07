import pytest

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from currency_converter import convert_currency

def test_abraham():
    result = convert_currency("USD", "USD", 50)
    assert result  == (50,1)


def test_abigail1():
    result = convert_currency("USD", "EUR", 1)
    assert result == (0.862, 0.862)