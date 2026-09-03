from typing import Optional

from pydantic import BaseModel
from rdflib import URIRef


class EnergyMarketOfferInfo(BaseModel):
    offer_id: Optional[int] = None
    market_id: int
    ts: int
    date_str: str
    offer_uri: Optional[str]
    range_id: int
    sequence: Optional[str]
    isp_unit: int
    isp_len: int
    update_ts: Optional[int] = None
    ext: Optional[str] = None


# TODO: add offer range to graphs and ontology
class EnergyMarketOfferDAO(BaseModel):
    offer_id: int
    isp_start: int
    cost_mwh: Optional[float]
    ts: int
    isp_len: int = 1

    # def get_value_timestamp(self, isp_unit):
    #     """
    #
    #     :param isp_unit: in minutes
    #     :return:
    #     """
    #     isp_unit_ms = isp_unit * 1000 * 60
    #     return self.ts + self.isp_start * isp_unit_ms

    @staticmethod
    def get_value_type() -> URIRef:
        from ubflex.rdf.saref.saref import PROPERTY_VALUE
        return PROPERTY_VALUE


class EnergyMarketOffer(BaseModel):
    offer_id: int
    isp_start: int
    cost_mwh: Optional[float]
    sequence: Optional[str] = None
    range_id: int
    # time created
    ts: int
    isp_len: int = 1

    # @staticmethod
    # def get_value_type() -> URIRef:
    #     from ubflex.rdf.saref.saref import PROPERTY_VALUE
    #     return PROPERTY_VALUE

    # def get_value_timestamp(self, isp_unit):
    #     """
    #
    #     :param isp_unit: in minutes
    #     :return:
    #     """
    #     isp_unit_ms = isp_unit * 1000 * 60
    #     return self.ts + self.isp_start * isp_unit_ms


class RangeInfo(BaseModel):
    range_id: Optional[int] = None
    min_value: Optional[float]
    max_value: Optional[float]
