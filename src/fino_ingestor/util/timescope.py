from datetime import date, timedelta
from enum import Enum, auto
from typing import Iterator, Optional, Self, Tuple

from dateutil.relativedelta import relativedelta
from pydantic import BaseModel, Field, model_validator


class Granularity(Enum):
    """期間の粒度を表す列挙型"""

    YEAR = auto()
    MONTH = auto()
    DAY = auto()


class TimeScope(BaseModel):
    """
    TimeScope model for collecting EDINET documents.
    - year: 年単位、月単位、日単位の指定する場合に指定する。
    - month: 月単位、日単位の指定する場合に指定する。（yearが必須）
    - day: 日単位の指定する場合に指定する。（year, monthが必須）
    ロジック（期間の変換、イテレーション）を内包します。
    """

    year: int = Field(ge=1900, le=2100)
    month: Optional[int] = Field(ge=1, le=12, default=None)
    day: Optional[int] = Field(ge=1, le=31, default=None)

    @model_validator(mode="after")
    def validate_time_scope(self) -> Self:
        if self.month is None and self.day is not None:
            raise ValueError("month is required if day is specified")
        else:
            return self

    @property  # @see: https://zenn.dev/yuto_mo/articles/29682f6b0c402c
    def granularity(self) -> Granularity:
        """
        TimeScopeの粒度を取得する

        Returns
        -------
        Granularity
            期間の粒度（YEAR, MONTH, DAY）

        Examples
        --------
        >>> timescope = TimeScope(year=2024, month=3, day=1)
        >>> timescope.granularity
        <Granularity.DAY: 3>
        """
        # yearは必須（int型）なので、monthとdayのみをチェック
        if self.month is not None and self.day is not None:
            return Granularity.DAY
        elif self.month is not None:
            return Granularity.MONTH
        else:
            # yearのみが指定されている場合
            return Granularity.YEAR

    @property
    def closest_day(self) -> date:
        """
        TimeScopeの最も近い日を取得する
        """
        if self.granularity == Granularity.DAY:
            return date(self.year, self.month or 1, self.day or 1)
        elif self.granularity == Granularity.MONTH:
            return date(self.year, self.month or 1, 1) + relativedelta(months=1) - timedelta(days=1)
        else:
            return date(self.year, 1, 1) + relativedelta(years=1) - timedelta(days=1)

    def to_range(self) -> Tuple[date, date]:
        """
        TimeScope を [start, end) の日付レンジに変換する

        Returns
        -------
        Tuple[date, date]
            (start, end) のタプル。endは半開区間（含まない）

        Examples
        --------
        >>> timescope = TimeScope(year=2024, month=3)
        >>> start, end = timescope.to_range()
        >>> start
        datetime.date(2024, 3, 1)
        >>> end
        datetime.date(2024, 3, 31)
        """

        if self.granularity == Granularity.DAY:
            # granularityがDAYの場合、monthとdayはNoneではない
            assert self.month is not None and self.day is not None  # noqa: S101
            start = date(self.year, self.month, self.day)
            end = start
        elif self.granularity == Granularity.MONTH:
            # granularityがMONTHの場合、monthはNoneではない
            assert self.month is not None  # noqa: S101
            start = date(self.year, self.month, 1)
            end = start + relativedelta(months=1) - timedelta(days=1)
        else:
            start = date(self.year, 1, 1)
            end = start + relativedelta(years=1) - timedelta(days=1)

        return start, end

    def iterate_by_day(self) -> Iterator[date]:
        """
        TimeScopeを日単位でイテレートする

        期間内のすべての日を日単位でイテレートします。
        粒度に関係なく、常に日単位で処理します。

        Yields
        ------
        date
            期間内の各日付（日単位）

        Examples
        --------
        >>> timescope = TimeScope(year=2024, month=3)
        >>> dates = list(timescope.iterate_by_day())
        >>> dates[0]
        datetime.date(2024, 3, 1)
        >>> dates[-1]
        datetime.date(2024, 3, 31)

        >>> timescope = TimeScope(year=2024)
        >>> dates = list(timescope.iterate_by_day())
        >>> len(dates)
        366  # 2024年はうるう年
        """
        start, end = self.to_range()
        current = start

        while current <= end:
            yield current
            current += timedelta(days=1)
