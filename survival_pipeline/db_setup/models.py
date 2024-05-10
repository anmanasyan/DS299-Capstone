"""
Database Schema
"""

import datetime as dt
import sqlalchemy as sql
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    Enum,
)
from sqlalchemy.sql import func

from database import Base, engine, _add_tables
from schema import CallStatus, MessageStatus


class Marz(Base):
    """
    Schema for Marz table.
    """

    __tablename__ = "marz"
    marz_id = Column(Integer, primary_key=True)
    marz = Column(String(50))


class ConsumerClient(Base):
    """
    Schema for ConsumerClient table.
    """

    __tablename__ = "consumer_client"
    cliid = Column(Integer, primary_key=True)
    gender = Column(String(10))
    birth_date = Column(DateTime)
    marz_id = Column(Integer, ForeignKey("marz.marz_id"))
    phone = Column(String(50))
    mobile_operator = Column(String(50))
    email = Column(String(50))


class ConsumerFamilyMembers(Base):
    """
    Schema for ConsumerFamilyMembers table.
    """

    __tablename__ = "consumer_family_members"
    row_id = Column(Integer, primary_key=True)
    cliid = Column(Integer, ForeignKey("consumer_client.cliid"))
    relation = Column(Integer)


class ConsumerMain(Base):
    """
    Schema for ConsumerMain table.
    """

    __tablename__ = "consumer_main"
    app_id = Column(Integer, primary_key=True)
    ap_date = Column(DateTime)
    cliid = Column(Integer, ForeignKey("consumer_client.cliid"))
    exp_int = Column(Float)
    status = Column(Integer)
    apl_stage = Column(Integer)
    origin_details = Column(Integer)
    npaidcount = Column(Integer)
    naplcount = Column(Integer)
    n_dpds = Column(Integer)
    max_dpd = Column(Integer)
    dsti_income = Column(Float)
    osm = Column(Float)
    n_salary = Column(Float)


class ConsumerHC(Base):
    """
    Schema for ConsumerHC table.
    """

    __tablename__ = "consumer_hc"
    loan_id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey("consumer_main.app_id"))
    issue_date = Column(DateTime)
    close_date = Column(DateTime)
    riskclass = Column(String(50))
    ficoscore = Column(Integer)
    contractperiod = Column(Integer)
    paidamount = Column(Float)
    initialamount = Column(Float)


class ECENGVehicleInfo(Base):
    """
    Schema for ECENGVehicleInfo table.
    """

    __tablename__ = "eceng_vehicle_info"
    row_id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey("consumer_main.app_id"))
    reg_num = Column(String(50))
    released = Column(String(10))
    vehicle_type = Column(String(100))
    model_name = Column(String(100))
    recording_date = Column(DateTime)
    fuel_type = Column(String(50))


class ECENGCESData(Base):
    """
    Schema for ECENGCESData table.
    """

    __tablename__ = "eceng_ces_data"
    row_id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey("consumer_main.app_id"))
    orderdate = Column(DateTime)
    inputdate = Column(DateTime)
    inquestdate = Column(DateTime)
    recoversum = Column(Float)
    inquestrem = Column(Float)
    inqueststate = Column(String(50))
    inquesttype = Column(String(300))


class SurvivalData(Base):
    """
    Schema for SurvivalData table.
    """

    __tablename__ = "survival_data"
    cliid = Column(Integer, ForeignKey("consumer_client.cliid"))
    app_id = Column(Integer, primary_key=True)
    ap_date = Column(DateTime)
    close_date = Column(DateTime)
    contractperiod = Column(Integer)
    paidamount = Column(Float)
    initialamount = Column(Float)
    exp_int = Column(Float)
    riskclass = Column(String(50))
    serveddays = Column(Integer)
    ficoscore = Column(Integer)
    npaidcount = Column(Integer)
    naplcount = Column(Integer)
    n_dpds = Column(Integer)
    max_dpd = Column(Integer)
    age = Column(Integer)
    gender = Column(String(10))
    n_salary = Column(Float)
    n_vehicles = Column(Integer)
    n_dahk = Column(Integer)
    n_dependents = Column(Integer)
    been_married = Column(Integer)
    sum_dahk = Column(Float)
    mobile_operator = Column(String(50))
    marz = Column(String(50))
    tenure = Column(Integer)
    event = Column(Boolean)


class SurvivalPredictions(Base):
    """
    Schema for SurvivalPredictions table.
    """

    __tablename__ = "survival_predictions"
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    date_created = Column(DateTime(timezone=True), server_default=func.now())
    cliid = Column(Integer, ForeignKey("consumer_client.cliid"))
    pred_period = Column(Integer)
    survival_probability = Column(Float)


class OutboundCalls(Base):
    """
    Schema for OutboundCalls table.
    """

    __tablename__ = "outbound_calls"
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    cliid = Column(Integer, ForeignKey("consumer_client.cliid"))
    phone = Column(String(50))
    date_called = Column(DateTime(timezone=True), server_default=func.now())
    call_status = Column(Enum(CallStatus))
    comment = Column(String(250))
    operator_name = Column(String(50))


class OutboundTexts(Base):
    """
    Schema for OutboundTexts table.
    """

    __tablename__ = "outbound_texts"
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    cliid = Column(Integer, ForeignKey("consumer_client.cliid"))
    phone = Column(String(50))
    date_sent = Column(DateTime(timezone=True), server_default=func.now())
    sent_status = Column(Enum(MessageStatus))
    content = Column(String(250))


class OutboundEmails(Base):
    """
    Schema for OutboundEmails table.
    """

    __tablename__ = "outbound_emails"
    row_id = Column(Integer, primary_key=True, autoincrement=True)
    cliid = Column(Integer, ForeignKey("consumer_client.cliid"))
    email = Column(String(50))
    date_sent = Column(DateTime(timezone=True), server_default=func.now())
    sent_status = Column(Enum(MessageStatus))
    content = Column(String(250))


# _add_tables(engine)

# recreate = True
# if recreate:
#     Base.metadata.drop_all(engine)
#     print('The Schema is deleted')
#     Base.metadata.create_all(bind=engine)
#     print('new schema is created')
