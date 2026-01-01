"""Tests for Period model."""

from datetime import date
from typing import Literal, TypeAlias

import pytest
from fino_core.domain.period import Granularity, Period


class TestPeriod:
    """Periodモデルのテスト"""

    YearArgs: TypeAlias = dict[Literal["year"], int]
    MonthArgs: TypeAlias = dict[Literal["year", "month"], int]
    DayArgs: TypeAlias = dict[Literal["year", "month", "day"], int]

    @pytest.fixture
    def period_year_args(self) -> YearArgs:
        return {
            "year": 2024,
        }

    @pytest.fixture
    def period_month_args(self) -> MonthArgs:
        return {
            "year": 2024,
            "month": 6,
        }

    @pytest.fixture
    def period_day_args(self) -> DayArgs:
        return {
            "year": 2024,
            "month": 3,
            "day": 15,
        }

    def test_create_period_year(self, period_year_args: YearArgs) -> None:
        """PeriodをYearのみで生成"""
        period = Period(**period_year_args)
        assert period.year == 2024
        assert period.month is None
        assert period.day is None
        assert period.granularity == Granularity.YEAR

        closest = period.closest_day
        assert closest == date(2024, 12, 31)

        start, end = period.to_range()
        assert start == date(2024, 1, 1)
        assert end == date(2024, 12, 31)

    def test_create_period_month(self, period_month_args: MonthArgs) -> None:
        """PeriodをYearとMonthで生成"""
        period = Period(**period_month_args)
        assert period.year == 2024
        assert period.month == 6
        assert period.day is None
        assert period.granularity == Granularity.MONTH

        closest = period.closest_day
        assert closest == date(2024, 6, 30)

        start, end = period.to_range()
        assert start == date(2024, 6, 1)
        assert end == date(2024, 6, 30)

    def test_create_period_date(self, period_day_args: DayArgs) -> None:
        """PeriodをYear、Month、Dayで生成"""
        period = Period(**period_day_args)
        assert period.year == 2024
        assert period.month == 3
        assert period.day == 15
        assert period.granularity == Granularity.DAY

        closest = period.closest_day
        assert closest == date(2024, 3, 15)

        start, end = period.to_range()
        assert start == date(2024, 3, 15)
        assert end == date(2024, 3, 15)

    def test_iterate_by_day_for_year(self, period_year_args: YearArgs) -> None:
        """Year: iterate_by_dayテスト"""
        period = Period(**period_year_args)
        dates = list(period.iterate_by_day())
        assert len(dates) == 366
        assert dates[0] == date(2024, 1, 1)
        assert dates[-1] == date(2024, 12, 31)

    def test_iterate_by_day_for_month(self, period_month_args: MonthArgs) -> None:
        """Month: iterate_by_dayテスト"""
        period = Period(**period_month_args)
        dates = list(period.iterate_by_day())
        assert len(dates) == 30
        assert dates[0] == date(2024, 6, 1)
        assert dates[-1] == date(2024, 6, 30)

    def test_iterate_by_day_for_day(self, period_day_args: DayArgs) -> None:
        """Day: iterate_by_dayテスト"""
        period = Period(**period_day_args)
        dates = list(period.iterate_by_day())
        assert len(dates) == 1
        assert dates[0] == date(2024, 3, 15)

    def test_closest_day_for_year(self) -> None:
        """Year: 閏年のテスト"""
        period = Period(year=2024, month=2)
        closest = period.closest_day
        # 2024年は閏年で2月の最後の日は29日
        assert closest == date(2024, 2, 29)

    def test_from_values_year_args(
        self, period_year_args: YearArgs, period_month_args: MonthArgs, period_day_args: DayArgs
    ) -> None:
        period = Period.from_values(values=period_year_args)
        """from_valuesテスト"""
        assert period.year == 2024
        assert period.month is None
        assert period.day is None

        period = Period.from_values(values=period_month_args)
        """from_valuesテスト"""
        assert period.year == 2024
        assert period.month == 6
        assert period.day is None

        period = Period.from_values(values=period_day_args)
        """from_valuesテスト"""
        assert period.year == 2024
        assert period.month == 3
        assert period.day == 15
