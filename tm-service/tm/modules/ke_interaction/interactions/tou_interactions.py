from typing import List

from ke_client import KIHolder

from tm.modules.ke_interaction.interactions.tou_model import TOUPriceQuery, TOUPriceInfoQuery
from tm.modules.ke_interaction.service import tou_service

ki = KIHolder()


@ki.answer("tou-price-info")
def on_price_info_request(ki_id: str, bindings: List[TOUPriceInfoQuery]):
    # tou_bindings = [TOUPriceInfoQuery(**b)   for b in   bindings]
    print("tou-price-info")
    tou_bindings = bindings
    prince_info_resp = tou_service.get_range_tou(tou_bindings, kb_id=ki.get_kb_id())
    # answer_bindings = [p.n3() for p in prince_info_resp]
    # print(answer_bindings)
    return prince_info_resp


@ki.answer("tou-price")
def on_price_request(ki_id: str, bindings: List[TOUPriceQuery]):
    print("tou-price")
    # print("on_price_request")
    # tou_bindings = [TOUPriceQuery(**b) for b in bindings]
    return tou_service.get_price(bindings, kb_id=ki.get_kb_id())
