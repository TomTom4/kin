from pydantic import UUID4, BaseModel


class KinModel(BaseModel):
    id: UUID4
