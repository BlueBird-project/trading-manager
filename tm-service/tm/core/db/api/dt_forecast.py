from abc import abstractmethod
from typing import List, Optional

from tm.models.digital_twin import DigitalTwinDAO


class DTForecastAPI:

    @abstractmethod
    def save(self, forecast_info: DTForecastInfoDAO) -> DTForecastInfoDAO:
        pass

    @abstractmethod
    def list_forecasts(self, ) -> List[DTForecastInfoDAO]:
        pass

    @abstractmethod
    def get(self, offer_id: int, market_id: Optional[int]) -> Optional[DTForecastInfoDAO]:
        pass
