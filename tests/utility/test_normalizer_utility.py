import pytest

from pynormalizenumexp.expression.base import NNumber
from pynormalizenumexp.utility.normalizer_utility import NormalizerUtility


@pytest.fixture(scope="class")
def normalizer_utility():
    return NormalizerUtility()


@pytest.fixture(scope="class")
def patterns():
    return {
        "あ": 0,
        "あい": 1,
        "あいう": 2,
        "いう": 3,
        "うえ": 4,
        "うえお": 5,
        "えお": 6,
        "いうえおあ": 7
    }


class TestNormalizerUtility:
    def test_replace_numbers_in_text(self, normalizer_utility: NormalizerUtility):
        numbers = [NNumber("30人", 2, 4), NNumber("三十五人", 9, 12)]
        res = normalizer_utility.replace_numbers_in_text("その30人がそれは三十五人でボボボ", numbers)
        assert res == "そのǂǂ人がそれはǂǂǂ人でボボボ"

    def test_prefix_search(self, normalizer_utility: NormalizerUtility, patterns):
        res = normalizer_utility.prefix_search("あいうえお", patterns)
        assert res == 2

        res = normalizer_utility.prefix_search("いうえおあいうえお", patterns)
        assert res == 7

        res = normalizer_utility.prefix_search("かきくけこ", patterns)
        assert res == -1
