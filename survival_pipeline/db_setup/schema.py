"""
This module defines SQLAlchemy models and Pydantic schemas for outbound calls and messages.
"""
from sqlalchemy import Enum
from enum import Enum
from pydantic import BaseModel

# Definition of CallStatus enumeration
class CallStatus(str, Enum):
    failed = "Failed"
    rejected = "Rejected"
    accepted = "Accepted"

# Definition of MessageStatus enumeration
class MessageStatus(str, Enum):
    delivered = "Delivered"
    failed = "Failed"

# Definition of OutboundCalls Pydantic model
class OutboundCalls(BaseModel):
    call_status: CallStatus
    comment: str
    operator_name: str


# Example usage:
if __name__ == "__main__":
    model = OutboundCalls(call_status=CallStatus.failed)
    print(model)
