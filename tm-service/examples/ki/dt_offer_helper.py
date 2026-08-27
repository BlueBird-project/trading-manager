import random
from threading import RLock, Thread
from typing import List, Optional, Dict, Callable, Any

from ke_client.utils import time_utils
from rdflib import URIRef, Literal

from examples.ki import dt_model
from examples.ki.dt_model import TMMarketOfferBindings, DTPnt
from tm.modules.ke_interaction.interactions.dam_model import MarketOfferInfoBindings
from tm.modules.ke_interaction.interactions.dt_model import DTTSUri, DTDPUri, DTDPRUri


class TMOffer:
    sequence: Optional[str] = None
    offer_uri: URIRef
    end_ts: int
    offer: Optional[List] = None
    forecast_uri: Optional[URIRef] = None

    def __init__(self, offer_uri: URIRef, end_ts: int, sequence: Optional[str] = None):
        self.offer_uri = offer_uri
        self.sequence = sequence
        self.end_ts = end_ts

    def __len__(self):
        if self.offer is None:
            return 96
        else:
            return len(self.offer)

    def get_offer(self):
        if self.offer is None:
            return []
        return self.offer


class OfferManager:
    offer_map: Dict[str, TMOffer]
    forecast_map: Dict[URIRef, List[DTPnt]]
    jobs: List[Callable]
    r_lock: RLock
    t: Thread = None

    def __init__(self):
        self.offer_map = {}
        self.forecast_map = {}
        self.r_lock = RLock()
        self.jobs = []

    def add_job(self, j: Callable):
        with self.r_lock:
            self.jobs.append(j)

    def set_forecast(self, ts_uri: URIRef, forecast_ts: List[DTPnt]):
        self.forecast_map[ts_uri] = forecast_ts

    def get_forecast_of(self, forecast_uri):
        tm_offer_lst: List[TMOffer] = [o for o in self.offer_map.values() if o.forecast_uri == forecast_uri]
        if len(tm_offer_lst) > 0:
            return tm_offer_lst[0]
        return None

    def get_forecast(self, ts_uri: URIRef) -> List[DTPnt]:
        if ts_uri not in self.forecast_map:
            return []
        return self.forecast_map[ts_uri]

    def get_job(self):
        with self.r_lock:
            if len(self.jobs) > 0:
                return self.jobs.pop()
            return None

    def start(self):
        def j():
            job = self.get_job()
            while job is not None:
                job()
                job = self.get_job()
            with self.r_lock:
                self.t = None

        with self.r_lock:
            if self.t is None:
                self.t = Thread(target=j)
                self.t.start()

    def set_offer_info(self, offer_uri: URIRef, end_ts: int, sequence: Optional[str] = None) -> TMOffer:
        if len(self.offer_map) > 10000:
            self.offer_map = {}
            self.forecast_map = {}
        if offer_uri not in self.offer_map:
            self.offer_map[offer_uri] = TMOffer(offer_uri=offer_uri, end_ts=end_ts, sequence=sequence)
        return self.offer_map[offer_uri]

    def set_offer(self, offer_uri: URIRef, offer: List[dt_model.TMMarketOfferBindings]):
        if offer_uri not in self.offer_map:
            self.set_offer_info(offer_uri=offer_uri, end_ts=time_utils.current_timestamp())
        tm = self.offer_map[offer_uri]
        tm.offer = offer

    def get_offer_info(self, offer_uri: URIRef,
                       get_info_handler: Optional[Callable[[], List[MarketOfferInfoBindings]]]):
        if offer_uri not in self.offer_map:
            if get_info_handler is not None:
                def t():
                    offer_info = get_info_handler()
                    for oi in offer_info:
                        self.set_offer_info(offer_uri=oi.offer_uri, sequence=oi.sequence, end_ts=oi.end_ts)

                self.add_job(t)
                self.start()

            return None
        return self.offer_map[offer_uri]

    def get_offer(self, offer_uri: URIRef, get_info_handler: Callable[[], List[MarketOfferInfoBindings]],
                  get_offer_handler: Callable[[], List[TMMarketOfferBindings]]):
        oi = self.get_offer_info(offer_uri=offer_uri, get_info_handler=get_info_handler)
        if oi.get_offer() is None:
            return []
        if len(oi.get_offer()) < 1:
            def t():
                offer = get_offer_handler()
                if len(offer) > 0:
                    self.set_offer(offer_uri=offer_uri, offer=offer)

            self.add_job(t)
            self.start()

            return None
        return self.offer_map[offer_uri].offer


def generate_random_timeseries(ts_uri: DTTSUri, kb_id, size=96) -> List[DTPnt]:
    cur_ts = ts_uri.ts_start
    isp = 0
    res = []
    while cur_ts <= ts_uri.ts_end and isp < size:
        isp += 1
        pnt = DTPnt(ts_uri=ts_uri.uri_ref,
                    dp=DTDPUri(prefix=kb_id, **ts_uri.__dict__, isp=isp).uri_ref,
                    ts=Literal(time_utils.xsd_from_ts(cur_ts)),
                    dpr=DTDPRUri(prefix=kb_id, **ts_uri.__dict__, isp=isp).uri_ref,
                    value=random.random() * 200 + 50)
        res.append(pnt)
        cur_ts += 60000 * 15
    return res


def generate_sample_forecast(ts_uri: DTTSUri, offer: List[TMMarketOfferBindings], kb_id, ) -> List[DTPnt]:
    cur_ts = ts_uri.ts_start
    isp = 0
    res = []

    def generate(v):
        if v is None:
            return -0.000123
        else:
            return float(v) * (-1)

    for o in offer:
        isp += 1
        pnt = DTPnt(ts_uri=ts_uri.uri_ref,
                    dp=DTDPUri(prefix=kb_id, **ts_uri.__dict__, isp=isp).uri_ref,
                    ts=Literal(time_utils.xsd_from_ts(cur_ts)),
                    dpr=DTDPRUri(prefix=kb_id, **ts_uri.__dict__, isp=isp).uri_ref,
                    value=Literal(generate(o.convert_value(o.value, float))))
        res.append(pnt)
        cur_ts += 60000 * 15
    return res


def _get_forecast_uri(command_uri: URIRef, sequence: Optional[Any], offer_end_ts: int) -> DTTSUri:
    ts_start = offer_end_ts
    ts_end = ts_start + 3600 * 1000 * 24
    ts_uri = DTTSUri(prefix=command_uri, sequence=sequence, ts_start=ts_start, ts_end=ts_end)
    return ts_uri


offer_manager = OfferManager()
