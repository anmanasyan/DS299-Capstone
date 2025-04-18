"""
Survival Analysis Modelling

This script performs survival analysis modelling using the 'Survival' class from 'modelling.survival_analysis' module.
It loads data from the 'survival_data' table using the 'from_sql_to_pandas' function from 'modelling.utils'.
Then, it dummifies categorical variables, fits an accelerated failure time (AFT) model, and predicts survival probabilities.
Finally, it saves the predictions to the 'survival_predictions' table in the database.
"""

from modelling.survival_analysis import Survival
from modelling.utils import from_sql_to_pandas
from modelling.database import engine

import pandas as pd

# Load data from the 'survival_data' table into a DataFrame
data = from_sql_to_pandas(engine, "survival_data")

# Dummify categorical variables
encode_cols = ["riskclass", "gender", "mobile_operator", "marz"]
survival_df = pd.get_dummies(
    data, columns=encode_cols, prefix=encode_cols, drop_first=False
)

# Define the variable has_dahk to balance the heavy skew of n_dahk (explained in survival_analysis.ipynb)
data["has_dahk"] = data["n_dahk"].apply(lambda x: 0 if x == 0 else 1)

# Drop unnecessary columns, columns with high correlation, and reference groups
# Specify which dummy columns to drop (reference categories and not meaningful ones)
columns_to_drop = [
    "riskclass_Ստանդարտ",
    "gender_Female",
    "mobile_operator_Ucom",
    "marz_ԵՐԵՎԱՆ",
    "app_id",
    "ap_date",
    "close_date",
    "max_dpd",
    "initialamount",
    "n_dahk",
    "sum_dahk",
]

# exclude the columns not needed for modelling
survival_df = survival_df.drop(columns=columns_to_drop)

# Instantiate the Survival class with relevant parameters
inst = Survival(
    duration_col="tenure", event_col="event", primary_col="cliid", data=survival_df
)

# Find the best AFT model
inst.find_best_aft_model()

# Fit the best AFT model and remove insignificant variables
aft = inst.fit_best_aft_model(remove_insignificant=True)
print(inst.model_summary(aft))
# Generate predictions using the best AFT model for 30 periods
pred = inst.predict_aft_model(aft, n_time_periods=30)
pred.rename(columns={"id": "cliid"}, inplace=True)

# Save predictions to the 'survival_predictions' table in the database
pred.to_sql("survival_predictions", con=engine, if_exists="append", index=False)
