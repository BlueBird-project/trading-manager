
from fastapi import APIRouter

from tm.core.healthcheck import service

router = APIRouter(prefix="")


@router.get("/",description="Check if service responds")
async def status():
    from ke_client.utils import time_utils 
    return time_utils.current_timestamp()

@router.get("/state",description="General status")
async def state():
    return service.get_service_state()


@router.get("/report",description="Detailed information about service")
async def report():
    return service.get_service_report()
