from abc import abstractmethod
from typing import List, Optional

from tm.core.db.api.dt_forecast import DTForecastAPI
from tm.core.db.postgresql.api_impl import QueryObject
from tm.models.digital_twin import DTForecastInfoDAO, DTForecastOfferDAO
from tm.utils import TimeSpan


class DTForecastAPIQueries(QueryObject):
    # todo: queries
    pass


class DTForecastAPImpl(DTForecastAPI):

    @abstractmethod
    def save(self, forecast_info: DTForecastInfoDAO) -> DTForecastInfoDAO:
        pass

    @abstractmethod
    def list_forecasts(self, ts: Optional[TimeSpan], dt_id: Optional[int]) -> List[DTForecastInfoDAO]:
        pass

    @abstractmethod
    def find_forecasts(self, ts: Optional[TimeSpan], dt_id: Optional[int], model_id: Optional[int], ) \
            -> List[DTForecastInfoDAO]:
        pass

    @abstractmethod
    def get(self, forecast_id: int) -> Optional[DTForecastInfoDAO]:
        pass

    @abstractmethod
    def get_offer(self, forecast_id: int) -> List[DTForecastOfferDAO]:
        pass

    @abstractmethod
    def get_offers(self, forecast_id: List[int]) -> List[DTForecastOfferDAO]:
        pass
