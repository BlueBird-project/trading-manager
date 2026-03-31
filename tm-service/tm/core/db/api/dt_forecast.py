from abc import abstractmethod
from typing import List, Optional, Dict

from tm.models.digital_twin import DTForecastInfoDAO, DTForecastOfferDAO
from tm.utils import TimeSpan


class DTForecastAPI:

    @abstractmethod
    def save(self, forecast_info: DTForecastInfoDAO) -> DTForecastInfoDAO:
        pass

    @abstractmethod
    def list_forecasts(self, ts: Optional[TimeSpan], job_id: Optional[int]) -> List[DTForecastInfoDAO]:
        pass

    @abstractmethod
    def find_forecasts(self, ts: Optional[TimeSpan], job_id: Optional[int], model_id: Optional[int]) \
            -> List[DTForecastInfoDAO]:
        pass

    @abstractmethod
    def get(self, forecast_id: int) -> Optional[DTForecastInfoDAO]:
        pass

    @abstractmethod
    def get_by_uri(self, forecast_uri: str) -> Optional[DTForecastInfoDAO]:
        pass

    @abstractmethod
    def get_offer(self, forecast_id: int) -> List[DTForecastOfferDAO]:
        pass

    @abstractmethod
    def get_offers(self, forecast_id: List[int]) -> List[DTForecastOfferDAO]:
        pass

    @abstractmethod
    def save_offer(self, forecast_offers: List[DTForecastOfferDAO]) -> List[Dict]:
        pass

    @abstractmethod
    def clear_forecast_offer(self, forecast_id) -> int:
        pass
