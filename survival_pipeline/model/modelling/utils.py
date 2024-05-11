"""
Utility functions
"""

import pandas as pd
from sqlalchemy import text


def map_to_group(values: list, series: pd.Series):
    """Define groups of a series based on a list of edge values.

    Args:
        values (list): A list of edges used as upper limits for defining groups.
        series (pd.Series): Pandas Series containing numerical data.

    Returns:
        pd.Series: A Series where each value is mapped to a group based on the provided edges.
    """
    # Define groups based on edges
    groups = [f"Group 1: {min(series)}-{values[0]}"]
    for i in range(len(values) - 1):
        groups.append(f"Group {i+2}: {values[i]}-{values[i+1]}")
    groups.append(f"Group {len(values)}: {values[-1]}-{max(series)}")

    def map_value_to_group(value: float):
        """Map values to groups.

        Args:
            value (float): A numerical value to be mapped to a group.

        Returns:
            str:  The group that the value belongs to.
        """
        for i, edge in enumerate(values):
            if value <= edge:
                return groups[i]
        return groups[-1]

    # Map values in the series to groups
    mapped_series = series.apply(map_value_to_group)
    return mapped_series


def from_sql_to_pandas(engine, table_name: str):
    """
    Retrieve data from a PostgreSQL database using SQLAlchemy and return it as a pandas DataFrame.

    Args:
        engine: Engine for the PostgreSQL database.
        table_name (str): The table_name we want to query.

    Returns:
        pandas DataFrame containing the retrieved data.
    """
    query = text(f"SELECT * FROM {table_name}")
    # Execute the query and fetch data into a DataFrame
    with engine.connect() as connection:
        df = pd.read_sql_query(query, connection)
    return df
