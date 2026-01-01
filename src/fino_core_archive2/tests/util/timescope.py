"""Tests for timescope model."""

from datetime import date
from typing import Literal, TypeAlias

import pytest
from fino_core.util.timescope import Granularity, TimeScope


class TestTimeScope:
    """TimeScopeモデルのテスト"""

    YearArgs: TypeAlias = dict[Literal["year"], int]
    MonthArgs: TypeAlias = dict[Literal["year", "month"], int]
    DayArgs: TypeAlias = dict[Literal["year", "month", "day"], int]

    @pytest.fixture
    def timescope_year_args(self) -> YearArgs:
        return {
            "year": 2024,
        }

    @pytest.fixture
    def timescope_month_args(self) -> MonthArgs:
        return {
            "year": 2024,
            "month": 6,
        }

    @pytest.fixture
    def timescope_day_args(self) -> DayArgs:
        return {
            "year": 2024,
            "month": 3,
            "day": 15,
        }

    def test_create_timescope_year(self, timescope_year_args: YearArgs) -> None:
        """TimeScopeをYearのみで生成"""
        timescope = TimeScope(**timescope_year_args)
        assert timescope.year == 2024
        assert timescope.month is None
        assert timescope.day is None
        assert timescope.granularity == Granularity.YEAR

        closest = timescope.closest_day
        assert closest == date(2024, 12, 31)

        start, end = timescope.to_range()
        assert start == date(2024, 1, 1)
        assert end == date(2024, 12, 31)

    def test_create_timescope_month(self, timescope_month_args: MonthArgs) -> None:
        """TimeScopeをYearとMonthで生成"""
        timescope = TimeScope(**timescope_month_args)
        assert timescope.year == 2024
        assert timescope.month == 6
        assert timescope.day is None
        assert timescope.granularity == Granularity.MONTH

        closest = timescope.closest_day
        assert closest == date(2024, 6, 30)

        start, end = timescope.to_range()
        assert start == date(2024, 6, 1)
        assert end == date(2024, 6, 30)

    def test_create_timescope_date(self, timescope_day_args: DayArgs) -> None:
        """TimeScopeをYear、Month、Dayで生成"""
        timescope = TimeScope(**timescope_day_args)
        assert timescope.year == 2024
        assert timescope.month == 3
        assert timescope.day == 15
        assert timescope.granularity == Granularity.DAY

        closest = timescope.closest_day
        assert closest == date(2024, 3, 15)

        start, end = timescope.to_range()
        assert start == date(2024, 3, 15)
        assert end == date(2024, 3, 15)

    def test_iterate_by_day_for_year(self, timescope_year_args: YearArgs) -> None:
        """Year: iterate_by_dayテスト"""
        timescope = TimeScope(**timescope_year_args)
        dates = list(timescope.iterate_by_day())
        assert len(dates) == 366
        assert dates[0] == date(2024, 1, 1)
        assert dates[-1] == date(2024, 12, 31)

    def test_iterate_by_day_for_month(self, timescope_month_args: MonthArgs) -> None:
        """Month: iterate_by_dayテスト"""
        timescope = TimeScope(**timescope_month_args)
        dates = list(timescope.iterate_by_day())
        assert len(dates) == 30
        assert dates[0] == date(2024, 6, 1)
        assert dates[-1] == date(2024, 6, 30)

    def test_iterate_by_day_for_day(self, timescope_day_args: DayArgs) -> None:
        """Day: iterate_by_dayテスト"""
        timescope = TimeScope(**timescope_day_args)
        dates = list(timescope.iterate_by_day())
        assert len(dates) == 1
        assert dates[0] == date(2024, 3, 15)

    def test_closest_day_for_year(self) -> None:
        """Year: 閏年のテスト"""
        timescope = TimeScope(year=2024, month=2)
        closest = timescope.closest_day
        # 2024年は閏年で2月の最後の日は29日
        assert closest == date(2024, 2, 29)

    def test_from_values_year_args(
        self,
        timescope_year_args: YearArgs,
        timescope_month_args: MonthArgs,
        timescope_day_args: DayArgs,
    ) -> None:
        timescope = TimeScope(year=timescope_year_args["year"])
        """from_valuesテスト"""
        assert timescope.year == 2024
        assert timescope.month is None
        assert timescope.day is None

        timescope = TimeScope(
            year=timescope_month_args["year"], month=timescope_month_args["month"]
        )
        """from_valuesテスト"""
        assert timescope.year == 2024
        assert timescope.month == 6
        assert timescope.day is None

        timescope = TimeScope(
            year=timescope_day_args["year"],
            month=timescope_day_args["month"],
            day=timescope_day_args["day"],
        )
        """from_valuesテスト"""
        assert timescope.year == 2024
        assert timescope.month == 3
        assert timescope.day == 15
