from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime

class MemberCreate(BaseModel):
    name: str
    identity_no: str

class MemberResponse(BaseModel):
    id: UUID
    name: str
    identity_no: str
    status: bool
    # ubah format database ke json
    model_config = ConfigDict(from_attributes=True)

class DistributionCreate(BaseModel):
    user_id: UUID
    member_id: UUID

class DistributionResponse(BaseModel):
    id: UUID
    member_id: UUID
    user_id: UUID
    date: datetime

    model_config = ConfigDict(from_attributes=True)