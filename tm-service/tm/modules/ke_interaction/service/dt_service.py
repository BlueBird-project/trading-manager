import logging
from collections import defaultdict
from typing import List, Dict

from ke_client.utils import to_json

from tm.models.digital_twin import DigitalTwinDAO, DTForecastInfoDAO, DTForecastOfferDAO
from tm.models.job_dao import JobDAO
from tm.models.market_offer import RangeInfo
from tm.modules.ke_interaction.interactions.dt_model import DigitalTwinInfo, DTTSInfo, DTPnt

from tm.utils import isp_unit_to_ms


def process(dt_info_list: List[DigitalTwinInfo]):
    # response: List[] = []
    # TODO: update all dt metadata ?
    for dt_info in dt_info_list:
        from tm.core.db.postgresql import dao_manager
        market = dao_manager.market_api.get_market(market_uri=dt_info.market_uri)
        if market is None:
            logging.error(f"Unknown market: {dt_info.market_uri}")
        else:
            db_job = dao_manager.job_api.get(command_uri=dt_info.command_uri)
            if db_job is None:
                job = dao_manager.job_api.save(JobDAO(command_uri=dt_info.command_uri, market_id=market.market_id,
                                                      job_name=dt_info.dt_uri,
                                                      ext=to_json({"market_uri": dt_info.market_uri})))
            else:
                job = db_job
            db_dt = dao_manager.dt_api.get(dt_uri=dt_info.dt_uri)
            if db_dt is None:
                dt = dao_manager.dt_api.save(
                    DigitalTwinDAO(dt_uri=dt_info.dt_uri, job_id=job.job_id))
            else:
                # TODO: dt_api.update(....)
                dt = db_dt
            # response.append(DigitalTwinInfoACK(dt_uri=URIRef(dt.dt_uri), command_uri=URIRef(job.command_uri)))
    # return response


def process_forecast_info(bindings: List[DTTSInfo]) -> List[DTForecastInfoDAO]:
    from tm.core.db.postgresql import dao_manager
    added_ts: List[DTForecastInfoDAO] = []
    # unlimited_range = dao_manager.offer_dao.get_range(None, None)
    # range_id = unlimited_range.range_id
    for b in bindings:
        min_power, max_power = b.get_power_limit()
        power_range = dao_manager.offer_dao.get_range(min_power, max_power)
        if power_range is None:
            logging.warning("Adding new power range")
            # TODO: prohibit autmatic range generation ?
            range_id = dao_manager.offer_dao.add_range(RangeInfo(min_value=min_power, max_value=max_power)).range_id
        else:
            range_id = power_range.range_id
        job = dao_manager.job_api.get(command_uri=b.command_uri)
        if job is None:
            logging.error(f"Job(Command) not found: {b.command_uri}")
        else:
            db_ts = dao_manager.forecast_api.get_by_uri(forecast_uri=b.ts_uri)
            if db_ts is not None:
                print(f"Forecast {b.ts_uri} have already been added")
                logging.info(f"Forecast {b.ts_uri} have already been added")
                #     TODO: update current instance in Db?
                added_ts.append(db_ts)
            else:
                new_ts = dao_manager.forecast_api.save(
                    # b.n3()
                    forecast_info=DTForecastInfoDAO(forecast_uri=b.ts_uri, job_id=job.job_id, ts=b.create_ts,
                                                    isp_unit=b.update_rate_min, sequence=b.get_sequence(),
                                                    isp_len=b.isp_len, range_id=range_id))
                logging.info(f"Forecast {b.ts_uri}:{new_ts.forecast_id} have been added")
                added_ts.append(new_ts)
    return added_ts


def process_forecast(forecast: List[DTPnt], clear: bool = True, ):
    from tm.core.db.postgresql import dao_manager
    grouped_bindings: Dict[str, List[DTPnt]] = defaultdict(list)
    saved_bindings = defaultdict(list)
    for f in forecast:
        grouped_bindings[str(f.ts_uri)].append(f)

    for ts_uri, forecast in grouped_bindings.items():
        forecast_info = dao_manager.forecast_api.get_by_uri(forecast_uri=ts_uri)
        if forecast_info is None:
            #     TODO:
            # raise Exception(f"Init offer info {offer_uri}")
            # TODO: add bg task to ask KE for offer details
            logging.error(f"Offer not registered {forecast_info}")
            # del grouped_bindings[offer_uri]
        else:
            if clear:
                # print(f"Updating with new offer {offer_uri}")
                logging.info(f"Removing old offer for {forecast_info}")
                dao_manager.forecast_api.clear_forecast_offer(forecast_id=forecast_info.forecast_id)
            isp_len_ms = isp_unit_to_ms(isp_unit=forecast_info.isp_unit)
            ts_start = forecast_info.ts
            forecast_dao: list = [None] * len(grouped_bindings[forecast_info.forecast_uri])
            for i, dp in enumerate(forecast):
                isp_start = (dp.ts_ms - ts_start) / isp_len_ms
                dp_dao = DTForecastOfferDAO(forecast_id=forecast_info.forecast_id, ts=forecast_info.ts,
                                            isp_start=isp_start, cost_mwh=dp.get_value(),
                                            isp_len=dp.isp_len(forecast_info.isp_unit))

                forecast_dao[i] = dp_dao
            saved_bindings[forecast_info.forecast_uri] = dao_manager.forecast_api.save_offer(
                forecast_offers=forecast_dao)

    return saved_bindings
    # forecast_id: int
    # isp_start: int
    # cost_mwh: Optional[float]
    # ts: int
    # isp_len: int = 1
