"""
Description:
This module provides endpoints for managing outbound communication with clients. 
It includes functionalities like retrieving client information, fetching survival data, creating calls, texts, and emails for clients.

Endpoints:
1. GET /get_client_info/: Retrieves client information by cliid(s).
2. GET /get_survival_data/: Retrieves survival data based on parameters.
3. POST /create_call/: Creates a new outbound call record for a client.
4. POST /create_text/: Creates new outbound text messages for one or more clients.
5. POST /create_email/: Creates new outbound email messages for one or more clients.
"""

# Importing libraries
import uvicorn
from typing import Union, List
from fastapi import FastAPI, Depends, HTTPException, Body, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime


from schema import OutboundCalls as OC, OutboundMessage as OM
from database import Base, engine, get_db
from models import (
    OutboundCalls,
    ConsumerClient,
    SurvivalPredictions,
    OutboundEmails,
    OutboundTexts,
)

# Creating FastAPI instance
app = FastAPI()


# Default endpoint
@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {"message": "API successfully initiated!"}


# Endpoint to retrieve client information by cliid
@app.get("/get_client_info/")
async def get_client_info(
    cliids: List[int] = Query(...), db: Session = Depends(get_db)
):
    """
    Retrieves client information by cliid(s).

    Parameters:
    - cliids (List[int]): List of cliids for which client information is to be retrieved.

    Returns:
    - List[Dict[str, Union[int, str]]]: List of dictionaries containing client information including cliid, phone, and email.
    """
    clients_info = (
        db.query(ConsumerClient.cliid, ConsumerClient.phone, ConsumerClient.email)
        .filter(ConsumerClient.cliid.in_(cliids))
        .all()
    )
    if clients_info:
        clients_data = [
            {"cliid": client[0], "phone": client[1], "email": client[2]}
            for client in clients_info
        ]
        return clients_data
    else:
        raise HTTPException(status_code=404, detail="No clients found")


# Endpoint to retrieve survival data
@app.get("/get_survival_data/")
async def get_survival_data(
    pred_period: int = Query(...),
    lower_limit: float = Query(0),
    upper_limit: float = Query(1),
    date_created: datetime = Query(None),  # Default to None initially
    db: Session = Depends(get_db),
):
    """
    Retrieves survival data based on parameters.

    Parameters:
    - pred_period (int): Prediction period for survival data.
    - lower_limit (float): Lower limit for survival probability.
    - upper_limit (float): Upper limit for survival probability.
    - date_created (datetime): Date when the survival data was created. If not provided, latest date_created is chosen.

    Returns:
    - List[Dict[str, Union[int, float]]]: List of dictionaries containing survival data including cliid and survival probability.
    """

    # If date_created is not provided, fetch the maximal date_created from SurvivalPredictions
    if date_created is None:
        max_date_created = db.query(func.max(SurvivalPredictions.date_created)).scalar()
        date_created = max_date_created if max_date_created else datetime.now()

    survival_data = (
        db.query(SurvivalPredictions.cliid, SurvivalPredictions.survival_probability)
        .filter(
            and_(
                SurvivalPredictions.pred_period == pred_period,
                SurvivalPredictions.survival_probability >= lower_limit,
                SurvivalPredictions.survival_probability <= upper_limit,
                SurvivalPredictions.date_created == date_created,
            )
        )
        .all()
    )

    # Format the query results into a list of dictionaries
    formatted_data = [
        {"cliid": row[0], "survival_probability": row[1]} for row in survival_data
    ]

    if formatted_data:
        return formatted_data
    else:
        raise HTTPException(
            status_code=404, detail="No survival data found for the given parameters"
        )


# Endpoint to create a new outbound call
@app.post("/create_call/", response_model=OC)
def create_call(Outbound: OC, cliid: int, db: Session = Depends(get_db)):
    """
    Creates a new outbound call record for a client.

    Parameters:
    - Outbound (OutboundCalls): Outbound call details including call status, comment, and operator name.
    - cliid (int): Client ID for whom the call is to be created.

    Returns:
    - OutboundCalls: Details of the newly created outbound call.
    """
    client_info = db.query(ConsumerClient).filter(ConsumerClient.cliid == cliid).first()

    # adding new Outbound Call in OutboundCalls table
    new_call = OutboundCalls(
        phone=client_info.phone,
        call_status=Outbound.call_status,
        comment=Outbound.comment,
        operator_name=Outbound.operator_name,
        cliid=client_info.cliid,
    )

    db.add(new_call)
    db.commit()
    db.refresh(new_call)
    return new_call


# Endpoint to create new outbound text message
@app.post("/create_text/", response_model=List[OM])
def create_text(
    Outbound: OM, cliids: List[int] = Body(...), db: Session = Depends(get_db)
):
    """
    Creates new outbound text messages for one or more clients.

    Parameters:
    - Outbound (OutboundMessage): Outbound text message details including sent status and content.
    - cliids (List[int]): List of client IDs for whom the text messages are to be created.

    Returns:
    - List[OutboundMessage]: List of details of the newly created outbound text messages.
    """

    texts_created = []

    for cliid in cliids:
        client_info = (
            db.query(ConsumerClient).filter(ConsumerClient.cliid == cliid).first()
        )

        if client_info:
            new_text = OutboundTexts(
                phone=client_info.phone,
                sent_status=Outbound.sent_status,
                content=Outbound.content,
                cliid=client_info.cliid,
            )

            db.add(new_text)
            db.commit()
            db.refresh(new_text)

            texts_created.append(new_text)
        else:
            raise HTTPException(
                status_code=404, detail=f"No client found with cliid {cliid}"
            )

    return texts_created


# Endpoint to create new outbound email messages
@app.post("/create_email/", response_model=List[OM])
def create_email(
    Outbound: OM, cliids: List[int] = Body(...), db: Session = Depends(get_db)
):
    """
    Creates new outbound email messages for one or more clients.

    Parameters:
    - Outbound (OutboundMessage): Outbound email message details including sent status and content.
    - cliids (List[int]): List of client IDs for whom the email messages are to be created.

    Returns:
    - List[OutboundMessage]: List of details of the newly created outbound email messages.
    """

    emails_created = []

    for cliid in cliids:
        client_info = (
            db.query(ConsumerClient).filter(ConsumerClient.cliid == cliid).first()
        )

        if client_info:
            new_email = OutboundEmails(
                email=client_info.email,
                sent_status=Outbound.sent_status,
                content=Outbound.content,
                cliid=client_info.cliid,
            )

            db.add(new_email)
            db.commit()
            db.refresh(new_email)

            emails_created.append(new_email)
        else:
            raise HTTPException(
                status_code=404, detail=f"No client found with cliid {cliid}"
            )

    return emails_created
