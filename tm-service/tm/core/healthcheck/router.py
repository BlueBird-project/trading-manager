
from fastapi import APIRouter

from tm.core.healthcheck import service

router = APIRouter(prefix="")


@router.get("/")
async def status():
    from effi_onto_tools.utils import time_utils
    return time_utils.current_timestamp()

@router.get("/state")
async def state():
    return service.get_service_state()


@router.get("/report")
async def report():
    return service.get_service_report()
