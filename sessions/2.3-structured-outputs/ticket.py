"""Session 2.3: the shape of one Nova Travel ticket, written as a Pydantic model."""
import json
from typing import Literal
from pydantic import BaseModel, Field


class Ticket(BaseModel):
    booking_id: str | None = Field(description="Like NT-4821. null if the customer gives none.")
    request_type: Literal["refund", "change", "question"]
    reason: str = Field(description="Why the customer writes, in a few words.")
    urgent: bool = Field(description="True if the customer needs help in the next two days.")


if __name__ == "__main__":  # run this file to see the JSON schema that Pydantic makes
    print(json.dumps(Ticket.model_json_schema(), indent=2))
