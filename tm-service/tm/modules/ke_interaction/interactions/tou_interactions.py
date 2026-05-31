from typing import List

from ke_client import KIHolder

from tm.modules.ke_interaction.interactions.tou_model import TOUPriceQuery,  TOUPriceInfoQueryFiltered
from tm.modules.ke_interaction.service import tou_service

tou_ki = KIHolder()


#
# @tou_ki.answer("tou-price-info")
# def on_price_info_request(ki_id: str, bindings: List[TOUPriceInfoQueryFiltered]):
#     tou_bindings = bindings
#     prince_info_resp = tou_service.get_range_tou_filtered(tou_bindings, kb_id=tou_ki.get_kb_id())
#     return prince_info_resp

@tou_ki.answer("tou-price-info-filtered")
def on_price_info_request(ki_id: str, bindings: List[TOUPriceInfoQueryFiltered]):
    tou_bindings = bindings
    prince_info_resp = tou_service.get_range_tou_filtered(tou_bindings, kb_id=tou_ki.get_kb_id())
    return prince_info_resp


@tou_ki.answer("tou-price")
def on_price_request(ki_id: str, bindings: List[TOUPriceQuery]):
    print("tou-price")
    return tou_service.get_price_filtered(bindings, kb_id=tou_ki.get_kb_id())
