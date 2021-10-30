import pytest

from pynormalizenumexp.expression.base import NNumber, NTime
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

    def test_shorten_place_holder_in_text(self, normalizer_utility: NormalizerUtility):
        res = normalizer_utility.shorten_place_holder_in_text("そのǂǂ人がそれはǂǂǂǂǂǂ人でボボボǂǂǂ")
        assert res == "そのǂ人がそれはǂ人でボボボǂ"

    def test_search_pattern_prefix(self, normalizer_utility: NormalizerUtility, patterns):
        res = normalizer_utility.search_pattern("あいうえお", patterns, "prefix")
        assert res == 2

        res = normalizer_utility.search_pattern("いうえおあいうえお", patterns, "prefix")
        assert res == 7

        res = normalizer_utility.search_pattern("かきくけこ", patterns, "prefix")
        assert res == -1

    def test_search_pattern_suffix(self, normalizer_utility: NormalizerUtility, patterns):
        res = normalizer_utility.search_pattern("あいうえお", patterns, "suffix")
        assert res == 5

        res = normalizer_utility.search_pattern("あいうえおあ", patterns, "suffix")
        assert res == 7

        res = normalizer_utility.search_pattern("かきくけこ", patterns, "suffix")
        assert res == -1

    def test_search_prefix_number_modifier(self, normalizer_utility: NormalizerUtility, patterns):
        res = normalizer_utility.search_prefix_number_modifier("あいうえおあ5あいうえおごごごごご", 6, patterns)
        assert res == 7

    def test_search_suffix_number_modifier(self, normalizer_utility: NormalizerUtility, patterns):
        res = normalizer_utility.search_suffix_number_modifier("あいうえおあ5あいうえおごごごごご", 7, patterns)
        assert res == 2

    def test_is_finite(self, normalizer_utility: NormalizerUtility):
        res = normalizer_utility.is_finite(99.999)
        assert res == True

        res = normalizer_utility.is_finite(float("inf"))
        assert res == False

        res = normalizer_utility.is_finite(-float("inf"))
        assert res == False

    def test_is_null_time(self, normalizer_utility: NormalizerUtility):
        res = normalizer_utility.is_null_time(NTime(value=float("inf")))
        assert res == True

        res = normalizer_utility.is_null_time(NTime(value=1))
        assert res == False

    def test_identify_time_detail(self, normalizer_utility: NormalizerUtility):
        t = NTime(year=1, month=1, day=1, hour=1, minute=1, second=1)
        res = normalizer_utility.identify_time_detail(t)
        assert res == "S"

        t = NTime(year=1, month=1, day=1, hour=1, minute=1, second=float("inf"))
        res = normalizer_utility.identify_time_detail(t)
        assert res == "M"

        t = NTime(year=1, month=1, day=1, hour=1, minute=float("inf"), second=float("inf"))
        res = normalizer_utility.identify_time_detail(t)
        assert res == "H"

        t = NTime(year=1, month=1, day=1, hour=float("inf"), minute=float("inf"), second=float("inf"))
        res = normalizer_utility.identify_time_detail(t)
        assert res == "d"

        t = NTime(year=1, month=1, day=float("inf"), hour=float("inf"), minute=float("inf"), second=float("inf"))
        res = normalizer_utility.identify_time_detail(t)
        assert res == "m"

        t = NTime(year=1, month=float("inf"), day=float("inf"),
                  hour=float("inf"), minute=float("inf"), second=float("inf"))
        res = normalizer_utility.identify_time_detail(t)
        assert res == "y"

        t = NTime(value=float("inf"))
        res = normalizer_utility.identify_time_detail(t)
        assert res == ""
