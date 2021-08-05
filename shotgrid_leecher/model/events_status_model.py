from pydantic import BaseModel, Field


class EventStatusModel(BaseModel):
    id: str = Field(alias="_id")
    last_processed_event_id: int = Field()
