# region uris
from ke_client import ki_split_uri, SplitURIBase

from tm.utils import TimeSpan


@ki_split_uri(uri_template=f"offer" + "/${offer_id}/${range_id}/${period_minutes}/${isp_start}")
class OfferDPSplitURI(SplitURIBase):
    range_id: int
    period_minutes: int
    offer_id: int
    isp_start: int


@ki_split_uri(uri_template=f"offer" + "/${offer_id}/${period_minutes}/${isp_start}")
class OfferDPSplitURIFiltered(SplitURIBase):
    period_minutes: int
    offer_id: int
    isp_start: int


@ki_split_uri(uri_template="tou_forecast/dp/${forecast_id}/${period_minutes}/${isp_start}")
class ForecastDPSplitURIFiltered(SplitURIBase):
    forecast_id: int
    period_minutes: int
    isp_start: int


# @ki_split_uri(uri_template="tou/${market_id}/${sequence}/${range_id}/${period_minutes}/${ts}")
# class TOUSplitURIFiltered(SplitURIBase):
#     range_id: int
#     period_minutes: int
#     ts: int
#     market_id: int
#     sequence: str
#
#     __EMPTY__ = "_"
#
#     @property
#     def time_span(self) -> TimeSpan:
#         return TimeSpan(ts_from=self.ts, ts_to=self.ts + self.period_minutes * 60000)
#
#     def __init__(self, sequence: Optional[str], **kwargs):
#         if sequence is None:
#             sequence = TOUSplitURIFiltered.__EMPTY__
#         super().__init__(sequence=sequence, **kwargs)
#
#     @property
#     def processed_sequence(self) -> Optional[str]:
#         if self.sequence == TOUSplitURIFiltered.__EMPTY__:
#             return None
#         return self.sequence
#
#     def __hash__(self):
#         return hash((self.range_id, self.period_minutes, self.ts, self.market_id, self.sequence))

@ki_split_uri(uri_template="tou/${offer_id}/${period_minutes}/${ts}")
class TOUSplitURIFiltered(SplitURIBase):
    period_minutes: int
    ts: int
    offer_id: int

    __EMPTY__ = "_"

    @property
    def time_span(self) -> TimeSpan:
        return TimeSpan(ts_from=self.ts, ts_to=self.ts + self.period_minutes * 60000)

    # def __init__(self, **kwargs):
    #     super().__init__(**kwargs)

    def __hash__(self):
        return hash((self.offer_id, self.period_minutes, self.ts))


@ki_split_uri(uri_template="tou_forecast/${forecast_id}/${period_minutes}/${ts}")
class TOUForecastSplitURIFiltered(SplitURIBase):
    forecast_id: int
    period_minutes: int
    ts: int


@ki_split_uri(uri_template="tou_range/${range_id}")
class TOURangeURI(SplitURIBase):
    range_id: int


@ki_split_uri(uri_template=f"tou_range_max" + "/${range_id}")
class TOURangeMaxURI(SplitURIBase):
    range_id: int


@ki_split_uri(uri_template=f"tou_range_min" + "/${range_id}")
class TOURangeMinURI(SplitURIBase):
    range_id: int


@ki_split_uri(uri_template="/commands/observe/${market_id}")
class TMCommandURI(SplitURIBase):
    market_id: int

# endregion
