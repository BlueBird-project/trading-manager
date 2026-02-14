from typing import Optional

from pydantic import BaseModel


class JobDAO(BaseModel):
    job_id: Optional[int] = None
    command_uri: str
    job_name: str
    job_description:Optional[str] = None
    update_ts: Optional[int] = None
    ext:Optional[str] = None
