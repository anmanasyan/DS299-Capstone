from sqlalchemy import create_engine, Column, Enum, Integer, DateTime
from enum import Enum
from pydantic import BaseModel


class CallStatus(str, Enum):
    failed = "Failed"
    rejected = "Rejected"
    accepted = "Accepted"


class MessageStatus(str, Enum):
    delivered = "Delivered"
    failed = "Failed"


class OutboundCalls(BaseModel):
    call_status: CallStatus
    comment: str
    operator_name: str


class OutboundMessage(BaseModel):
    sent_status: MessageStatus
    content: str


# Example usage:
if __name__ == "__main__":
    model = OutboundCalls(call_status=CallStatus.failed)
    print(model)
