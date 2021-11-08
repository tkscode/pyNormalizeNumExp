import pytest

from pynormalizenumexp.expression.base import INF
from pynormalizenumexp.normalize_numexp import Expression, NormalizeNumexp, Time


@pytest.fixture(scope="class")
def normalize_numexp():
    return NormalizeNumexp("ja")


class TestNormalizeNumexp:
    def test_normalize(self, normalize_numexp: NormalizeNumexp):
        res = normalize_numexp.normalize("1911年から2011年の間、その100年間において、9.3万人もの死傷者がでた。")
        expect = [
            Expression(
                type="abstime", original_expr="1911年から2011年", position_start=0, position_end=12, counter="none",
                value_lower_bound=Time(1911, INF, INF, INF, INF, INF),
                value_upper_bound=Time(2011, -INF, -INF, -INF, -INF, -INF), options=[]
            ),
            Expression(
                type="duration", original_expr="100年間", position_start=17, position_end=22, counter="none",
                value_lower_bound=Time(100, INF, INF, INF, INF, INF),
                value_upper_bound=Time(100, -INF, -INF, -INF, -INF, -INF), options=[]
            ),
            Expression(
                type="numerical", original_expr="9.3万人", position_start=27, position_end=32, counter="人",
                value_lower_bound=93000, value_upper_bound=93000, options=[]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("15年前、戦争があった")
        expect = [
            Expression(
                type="reltime", original_expr="15年前", position_start=0, position_end=4, counter="none",
                value_lower_bound_abs=Time(INF, INF, INF, INF, INF, INF),
                value_upper_bound_abs=Time(-INF, -INF, -INF, -INF, -INF, -INF),
                value_lower_bound_rel=Time(-15, INF, INF, INF, INF, INF),
                value_upper_bound_rel=Time(-15, -INF, -INF, -INF, -INF, -INF), options=[]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("昨年3月、僕たち２人は結婚した")
        expect = [
            Expression(
                type="reltime", original_expr="昨年3月", position_start=0, position_end=4, counter="none",
                value_lower_bound_abs=Time(INF, 3, INF, INF, INF, INF),
                value_upper_bound_abs=Time(-INF, 3, -INF, -INF, -INF, -INF),
                value_lower_bound_rel=Time(-1, INF, INF, INF, INF, INF),
                value_upper_bound_rel=Time(-1, -INF, -INF, -INF, -INF, -INF), options=[]
            ),
            Expression(
                type="numerical", original_expr="２人", position_start=8, position_end=10, counter="人",
                value_lower_bound=2, value_upper_bound=2, options=[]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("131.1ポイントというスコアを叩き出した")
        expect = [
            Expression(
                type="numerical", original_expr="131.1ポイント", position_start=0, position_end=9, counter="ポイント",
                value_lower_bound=131.1, value_upper_bound=131.1, options=[]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("午後3時45分に待ち合わせ")
        expect = [
            Expression(
                type="abstime", original_expr="午後3時45分", position_start=0, position_end=7, counter="none",
                value_lower_bound=Time(INF, INF, INF, 15, 45, INF),
                value_upper_bound=Time(-INF, -INF, -INF, 15, 45, -INF), options=[]
            )
        ]
        assert res == expect

    def test_normalize_day_of_week(self, normalize_numexp: NormalizeNumexp):
        res = normalize_numexp.normalize("5月3日(水)")
        expect = [
            Expression(
                type="abstime", original_expr="5月3日(水)", position_start=0, position_end=7, counter="none",
                value_lower_bound=Time(INF, 5, 3, INF, INF, INF),
                value_upper_bound=Time(-INF, 5, 3, -INF, -INF, -INF), options=["Wed"]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("2001/3/3 Sat")
        expect = [
            Expression(
                type="abstime", original_expr="2001/3/3 Sat", position_start=0, position_end=12, counter="none",
                value_lower_bound=Time(2001, 3, 3, INF, INF, INF),
                value_upper_bound=Time(2001, 3, 3, -INF, -INF, -INF), options=["Sat"]
            )
        ]
        assert res == expect

    def test_normalize_real(self, normalize_numexp: NormalizeNumexp):
        res = normalize_numexp.normalize("【今日から開催】The Fruits of Adventures @ ZEIT-FOTO SALON(東京・京橋)  4/26(Tue)まで")
        expect = [
            Expression(
                type="reltime", original_expr="今日", position_start=1, position_end=3, counter="none",
                value_lower_bound_abs=Time(INF, INF, INF, INF, INF, INF),
                value_upper_bound_abs=Time(-INF, -INF, -INF, -INF, -INF, -INF),
                value_lower_bound_rel=Time(INF, INF, 0, INF, INF, INF),
                value_upper_bound_rel=Time(-INF, -INF, 0, -INF, -INF, -INF), options=[]
            ),
            Expression(
                type="abstime", original_expr="4/26(Tue)まで", position_start=59, position_end=70, counter="none",
                value_lower_bound=Time(INF, 4, 26, INF, INF, INF),
                value_upper_bound=Time(-INF, 4, 26, -INF, -INF, -INF), options=["Tue"]
            )
        ]
        assert res == expect

    def test_normalize_inappropriate_range(self, normalize_numexp: NormalizeNumexp):
        res = normalize_numexp.normalize("中国から30匹の鳥がきた")
        expect = [
            Expression(
                type="numerical", original_expr="30匹", position_start=4, position_end=7, counter="匹",
                value_lower_bound=30, value_upper_bound=30, options=[]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("30匹からのプレゼント")
        expect = [
            Expression(
                type="numerical", original_expr="30匹", position_start=0, position_end=3, counter="匹",
                value_lower_bound=30, value_upper_bound=30, options=[]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("一万年と二千年前からああああ")
        expect = [
            Expression(
                type="duration", original_expr="一万年", position_start=0, position_end=3, counter="none",
                value_lower_bound=Time(10000, INF, INF, INF, INF, INF),
                value_upper_bound=Time(10000, -INF, -INF, -INF, -INF, -INF), options=[]
            ),
            Expression(
                type="reltime", original_expr="二千年前", position_start=4, position_end=8, counter="none",
                value_lower_bound_abs=Time(INF, INF, INF, INF, INF, INF),
                value_upper_bound_abs=Time(-INF, -INF, -INF, -INF, -INF, -INF),
                value_lower_bound_rel=Time(-2000, INF, INF, INF, INF, INF),
                value_upper_bound_rel=Time(-2000, -INF, -INF, -INF, -INF, -INF), options=[]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("話をしよう。あれは今から36万年前………いや、1万4000年前だったか。")
        expect = [
            Expression(
                type="reltime", original_expr="36万年前", position_start=12, position_end=17, counter="none",
                value_lower_bound_abs=Time(INF, INF, INF, INF, INF, INF),
                value_upper_bound_abs=Time(-INF, -INF, -INF, -INF, -INF, -INF),
                value_lower_bound_rel=Time(-360000, INF, INF, INF, INF, INF),
                value_upper_bound_rel=Time(-360000, -INF, -INF, -INF, -INF, -INF), options=[]
            ),
            Expression(
                type="reltime", original_expr="1万4000年前", position_start=23, position_end=31, counter="none",
                value_lower_bound_abs=Time(INF, INF, INF, INF, INF, INF),
                value_upper_bound_abs=Time(-INF, -INF, -INF, -INF, -INF, -INF),
                value_lower_bound_rel=Time(-14000, INF, INF, INF, INF, INF),
                value_upper_bound_rel=Time(-14000, -INF, -INF, -INF, -INF, -INF), options=[]
            )
        ]
        assert res == expect

    def test_normalize_inappropriate_string(self, normalize_numexp: NormalizeNumexp):
        res = normalize_numexp.normalize("一体それがどうしたというのだね。九州。四国。")
        assert res == []

    def test_normalize_inappropriate_prefix(self, normalize_numexp: NormalizeNumexp):
        res = normalize_numexp.normalize("ver2.3.4。ver２．３。")
        assert res == []

    def test_normalize_inappropriate_abstime(self, normalize_numexp: NormalizeNumexp):
        res = normalize_numexp.normalize("080-6006-4451。ver2.0。")
        assert res == []

        res = normalize_numexp.normalize("198999年30月41日。")
        expect = [
            Expression(
                type="duration", original_expr="198999年", position_start=0, position_end=7, counter="none",
                value_lower_bound=Time(198999, INF, INF, INF, INF, INF),
                value_upper_bound=Time(198999, -INF, -INF, -INF, -INF, -INF), options=[]
            ),
            Expression(
                type="duration", original_expr="30月", position_start=7, position_end=10, counter="none",
                value_lower_bound=Time(INF, 30, INF, INF, INF, INF),
                value_upper_bound=Time(-INF, 30, -INF, -INF, -INF, -INF), options=[]
            ),
            Expression(
                type="duration", original_expr="41日", position_start=10, position_end=13, counter="none",
                value_lower_bound=Time(INF, INF, 41, INF, INF, INF),
                value_upper_bound=Time(-INF, -INF, 41, -INF, -INF, -INF), options=[]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("09年5月。99年5月")
        expect = [
            Expression(
                type="abstime", original_expr="09年5月", position_start=0, position_end=5, counter="none",
                value_lower_bound=Time(2009, 5, INF, INF, INF, INF),
                value_upper_bound=Time(2009, 5, -INF, -INF, -INF, -INF), options=[]
            ),
            Expression(
                type="abstime", original_expr="99年5月", position_start=6, position_end=11, counter="none",
                value_lower_bound=Time(1999, 5, INF, INF, INF, INF),
                value_upper_bound=Time(1999, 5, -INF, -INF, -INF, -INF), options=[]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("西暦99年5月")
        expect = [
            Expression(
                type="abstime", original_expr="西暦99年5月", position_start=0, position_end=7, counter="none",
                value_lower_bound=Time(99, 5, INF, INF, INF, INF),
                value_upper_bound=Time(99, 5, -INF, -INF, -INF, -INF), options=[]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("1.2.2 2-2-2")
        assert res == []

    def test_normalize_inappropriate_url(self, normalize_numexp: NormalizeNumexp):
        res = normalize_numexp.normalize("http://3gl3molggg.com")
        assert res == []

    def test_normalize_su(self, normalize_numexp: NormalizeNumexp):
        res = normalize_numexp.normalize("数十人が十数人と喧嘩して、百数十円落とした")
        expect = [
            Expression(
                type="numerical", original_expr="数十人", position_start=0, position_end=3, counter="人",
                value_lower_bound=10, value_upper_bound=90, options=[]
            ),
            Expression(
                type="numerical", original_expr="十数人", position_start=4, position_end=7, counter="人",
                value_lower_bound=11, value_upper_bound=19, options=[]
            ),
            Expression(
                type="numerical", original_expr="百数十円", position_start=13, position_end=17, counter="円",
                value_lower_bound=110, value_upper_bound=190, options=[]
            )
        ]
        assert res == expect

    def test_normalize_range(self, normalize_numexp: NormalizeNumexp):
        res = normalize_numexp.normalize("2012/4/3~6に行われる")
        expect = [
            Expression(
                type="abstime", original_expr="2012/4/3~6", position_start=0, position_end=10, counter="none",
                value_lower_bound=Time(2012, 4, 3, INF, INF, INF),
                value_upper_bound=Time(2012, 4, 6, -INF, -INF, -INF), options=[]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("2012/4/3~2012/4/6に行われる")
        expect = [
            Expression(
                type="abstime", original_expr="2012/4/3~2012/4/6", position_start=0, position_end=17, counter="none",
                value_lower_bound=Time(2012, 4, 3, INF, INF, INF),
                value_upper_bound=Time(2012, 4, 6, -INF, -INF, -INF), options=[]
            )
        ]
        assert res == expect

    def test_normalize_wari(self, normalize_numexp: NormalizeNumexp):
        res = normalize_numexp.normalize("彼の打率は3割4分5厘だ")
        expect = [
            Expression(
                type="numerical", original_expr="3割4分5厘", position_start=5, position_end=11, counter="%",
                value_lower_bound=34.5, value_upper_bound=34.5, options=[]
            )
        ]
        assert res == expect

    def test_normalize_return_dict(self, normalize_numexp: NormalizeNumexp):
        res = normalize_numexp.normalize("15年前、戦争があった", as_dict=True)
        expect = [
            dict(
                type="reltime", original_expr="15年前", position_start=0, position_end=4, counter="none",
                value_lower_bound=None, value_upper_bound=None,
                value_lower_bound_abs=dict(year=INF, month=INF, day=INF, hour=INF, minute=INF, second=INF),
                value_upper_bound_abs=dict(year=-INF, month=-INF, day=-INF, hour=-INF, minute=-INF, second=-INF),
                value_lower_bound_rel=dict(year=-15, month=INF, day=INF, hour=INF, minute=INF, second=INF),
                value_upper_bound_rel=dict(year=-15, month=-INF, day=-INF, hour=-INF, minute=-INF, second=-INF),
                options=[]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("2012/4/3~6に行われる", as_dict=True)
        expect = [
            dict(
                type="abstime", original_expr="2012/4/3~6", position_start=0, position_end=10, counter="none",
                value_lower_bound=dict(year=2012, month=4, day=3, hour=INF, minute=INF, second=INF),
                value_upper_bound=dict(year=2012, month=4, day=6, hour=-INF, minute=-INF, second=-INF),
                value_lower_bound_abs=None, value_upper_bound_abs=None,
                value_lower_bound_rel=None, value_upper_bound_rel=None,
                options=[]
            )
        ]
        assert res == expect

        res = normalize_numexp.normalize("彼の打率は3割4分5厘だ", as_dict=True)
        expect = [
            dict(
                type="numerical", original_expr="3割4分5厘", position_start=5, position_end=11, counter="%",
                value_lower_bound=34.5, value_upper_bound=34.5,
                value_lower_bound_abs=None, value_upper_bound_abs=None,
                value_lower_bound_rel=None, value_upper_bound_rel=None,
                options=[]
            )
        ]
        assert res == expect
