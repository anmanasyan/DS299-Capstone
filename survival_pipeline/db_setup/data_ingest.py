"""
Data Ingestion

This module provides functionalities for ingesting data into database tables and executing stored procedures.
"""

from sqlalchemy import text
import pandas as pd
from os.path import join

from database import engine, _add_tables
from models import (
    Marz,
    ConsumerClient,
    ConsumerFamilyMembers,
    ConsumerMain,
    ConsumerHC,
    ECENGVehicleInfo,
    ECENGCESData,
    SurvivalData,
    SurvivalPredictions,
    OutboundCalls,
    OutboundTexts,
    OutboundEmails,
)


def create_stored_procedure(engine, filepath, procedure_name):
    """
    Creates a stored procedure in the database from an SQL file.

    Args:
    - engine: SQLAlchemy Engine instance representing the database connection.
    - filepath (str): Path to the directory containing the SQL file.
    - procedure_name (str): Name of the stored procedure and SQL file.

    Returns:
    - sqlalchemy.text: Text representation of the SQL query.
    """

    with engine.connect() as connection:
        # Define the SQL query for selecting the most recent project
        with open(join(filepath, f"{procedure_name}.sql"), "r") as file:
            query = text(file.read())
        connection.execute(query)
        connection.commit()
        return query


def executeprocedure(engine, procedure_name):
    """
    Executes a stored procedure in the database.

    Args:
    - engine: SQLAlchemy Engine instance representing the database connection.
    - procedure_name (str): Name of the stored procedure to execute.

    Returns:
    - str: Message indicating successful execution of the procedure.
    """
    with engine.connect() as connection:
        connection.execute(text(f"CALL public.{procedure_name}()"))
        connection.commit()
    return f"Procedure {procedure_name} executed!"


def load_csv_to_table(table_name, csv_path):
    """
    Load data from a CSV file into a database table.

    Args:
    - table_name: Name of the database table.
    - csv_path: Path to the CSV file containing data.

    Returns:
    - None
    """
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, con=engine, if_exists="append", index=False)


# Initiating Database Tables
_add_tables(engine)

# Define a list containing table names and their corresponding CSV file paths
tables_to_load = [
    "marz",
    "consumer_client",
    "consumer_family_members",
    "consumer_main",
    "consumer_hc",
    "eceng_vehicle_info",
    "eceng_ces_data",
]

# Loop through the list of tables and CSV file paths, and load each CSV into its corresponding table
for table in tables_to_load:
    try:
        load_csv_to_table(table, join("data/", f"{table}.csv"))
    except Exception as e:
        print(f"Failed to ingest table {table}. Moving to the next!")

print("Tables are populated.")

# Creating and executing the procedure for populating the survival_data table
proc = "update_survival_data"
create_stored_procedure(engine, "sql_queries", proc)
executeprocedure(engine, proc)
print(f"Procedure {proc} is executed")
