"""
Defines a class called Survival for implementing Kaplan-Meier and Accelerated-Failure Time (AFT) models.
"""
import pandas as pd
import numpy as np
from .utils import map_to_group
import matplotlib.pyplot as plt
from lifelines import (
    KaplanMeierFitter,
    WeibullAFTFitter,
    LogLogisticAFTFitter,
    LogNormalAFTFitter,
)


class Survival:
    def __init__(
        self, duration_col: str, event_col: str, primary_col: str, data: pd.DataFrame
    ):
        """Initializes the Survival analysis model with the provided data.

        Args:
            duration_col (str): Column name for the 'duration' or 'time' data
            event_col (str): Column name for the 'event occurred' data.
            primary_col (str): Column name for the primary key of the data.
            data (pd.DataFrame): Pandas DataFrame containing the survival data.
        """
        self.duration_col = duration_col
        self.event_col = event_col
        self.primary_col = primary_col
        self.data = data
        self.covariates = data.drop(
            columns=[duration_col, event_col, primary_col]
        ).columns.tolist()
        self.km_fitter = KaplanMeierFitter()
        self.aft_fitter = None

    def fit_kaplan_meier(self):
        """Fits a Kaplan-Meier model to the data.

        Returns:
            lifelines.KaplanMeierFitter: A fitted Kaplan-Meier model.
        """
        model = self.km_fitter.fit(
            self.data[self.duration_col], self.data[self.event_col]
        )
        return model

    def plot_kaplan_meier(self, density: bool = False):
        """Plots the Kaplan-Meier survival or cumulative density curve."""
        self.fit_kaplan_meier()
        if density == False:
            self.km_fitter.plot_survival_function()
            plt.title("Kaplan-Meier Survival Curve")
            plt.ylabel("Survival Probability")
        else:
            self.km_fitter.plot_cumulative_density()
            plt.title("Kaplan-Meier Cumulative Density Curve")
            plt.ylabel("Cumulative Density")

        plt.xlabel("Time")
        plt.show()

    def plot_kaplain_meier_grouped(
        self, covariate: str, values: list = [], density: bool = False
    ):
        """Plot Kaplan-Meier survival curves or cumulative density curves grouped by a specified covariate.

        Args:
            covariate (str): The name of the covariate to group by.
            values (list, optional): List of values corresponding to the covariate for grouping. If provided, the data will be grouped based on these values.
                                    Not required for categorical covariates as grouping is done automatically. Defaults to an empty list.
            density (bool, optional): If True, plot cumulative density curves; if False, plot survival probability curves. Defaults to False.
        """
        ax = plt.subplot(111)

        if density:
            title_prefix = "Cumulative Density"
            ylabel = "Cumulative Density"
            plot_func = self.km_fitter.plot_cumulative_density
        else:
            title_prefix = "Survival Probability"
            ylabel = "Survival Probability"
            plot_func = self.km_fitter.plot_survival_function

        plt.title(f"{title_prefix} Grouped by {covariate}", fontsize=14)

        # Prepare data
        survival_df = self.data.drop(columns=[self.primary_col])
        if values:
            survival_df["group"] = map_to_group(values, self.data[covariate])
        else:
            survival_df["group"] = self.data[covariate]

        # Group and plot
        for name, grouped_df in survival_df.groupby("group"):
            self.km_fitter.fit(
                grouped_df[self.duration_col], grouped_df[self.event_col], label=name
            )
            plot_func(ax=ax)

        plt.ylabel(ylabel, fontsize=13)

        # Remove background grid
        plt.grid(False)

        # Add x label
        plt.xlabel("Time", fontsize=13)
        plt.show()

    def find_best_aft_model(self):
        """Finds the best Accelerated Failure Time (AFT) model among Weibull, Log-Normal, and Log-Logistic distributions.
        This method fits each AFT model to the data and selects the model with the lowest Akaike Information Criterion (AIC).

        Returns:
            aft_fitter: The fitted AFT model (either WeibullAFTFitter, LogNormalAFTFitter, or LogLogisticAFTFitter)
                        that best fits the data based on AIC.

        """

        weibull_fitter = WeibullAFTFitter()
        log_normal_fitter = LogNormalAFTFitter()
        log_logistic_fitter = LogLogisticAFTFitter()

        # Remove primary key column
        survival_df = self.data.drop(columns=[self.primary_col])

        # Handle zero values in the duration column
        survival_df[self.duration_col] = survival_df[self.duration_col].replace(
            0, 0.0001
        )

        models = {
            "Weibull": weibull_fitter,
            "Log-Normal": log_normal_fitter,
            "Log-Logistic": log_logistic_fitter,
        }

        best_aic = float("inf")
        best_model = None

        for model_name, model in models.items():
            model.fit(
                survival_df, duration_col=self.duration_col, event_col=self.event_col
            )
            aic = model.AIC_

            if aic < best_aic:
                best_aic = aic
                best_model = model_name

        self.aft_fitter = models[best_model]
        print(f"Best distribution: {best_model} (AIC: {best_aic})")
        return self.aft_fitter

    def fit_best_aft_model(
        self, remove_insignificant: bool = False, alpha: float = 0.05
    ):
        """Fits the best Accelerated Failure Time (AFT) model to the data.

        This method fits the previously selected best AFT model to the survival data.

        Args:
            remove_insignificant (bool): Whether to remove insignificant variables based on the specified alpha level (default is False).
            alpha (float): Significance level for determining the insignificance of variables (default is 0.05).


        Returns:
            aft_model: The fitted AFT model (either WeibullAFTFitter, LogNormalAFTFitter, or LogLogisticAFTFitter).
        """

        if self.aft_fitter is None:
            print("You need to fit the best distribution first.")
            return

        # Remove primary key column
        survival_df = self.data.drop(columns=[self.primary_col])

        # Handle zero values in the duration column
        survival_df[self.duration_col] = survival_df[self.duration_col].replace(
            0, 0.0001
        )

        model = self.aft_fitter.fit(survival_df, self.duration_col, self.event_col)

        if remove_insignificant:
            p_values = model.summary["p"]
            insignificant_covariates = (
                p_values[
                    (p_values.index.get_level_values("covariate") != "Intercept")
                    & (p_values > alpha)
                ]
                .dropna()
                .index.get_level_values("covariate")
                .unique()
            )
            survival_df = survival_df.drop(columns=insignificant_covariates)
            model = self.aft_fitter.fit(survival_df, self.duration_col, self.event_col)

        return model

    def model_summary(self, aft_model):
        """Prints a summary of the fitted Accelerated Failure Time (AFT) model.

        Args:
            aft_model: An instance of a fitted AFT model (WeibullAFTFitter, LogNormalAFTFitter, or LogLogisticAFTFitter).

        Returns:
            str: A summary of the fitted AFT model.
        """
        return aft_model.print_summary(3)

    def plot_aft_model(self, aft_model):
        """Plot a visual representation of the coefficients (i.e. log accelerated failure rates).

        Args:
            aft_model: An instance of a fitted AFT model (WeibullAFTFitter, LogNormalAFTFitter, or LogLogisticAFTFitter).

        """
        aft_model.plot()
        plt.show()
    
    def partial_effects_on_outcome(
         self, aft_model, covariate: str, values: list, type: str = "cumulative_hazard", ax=None
    ):
        """Produces a plot comparing the baseline curve of the model versus what happens when a covariate is varied over values in a group.

        Args:
            aft_model: An instance of a fitted AFT model (WeibullAFTFitter, LogNormalAFTFitter, or LogLogisticAFTFitter).
            covariate (str): A string representing the covariate we wish to vary.
            values (list): A list of the specific values we wish the covariate to take on.
            type (str, optional): One of “survival_function”, or “cumulative_hazard”. Defaults to 'cumulative_hazard'.
            ax (matplotlib.axes.Axes, optional): The axes to plot the partial effects on. If not provided, a new figure will be created.
        """
        if ax is None:
            _, ax = plt.subplots(1, 1)

        aft_model.plot_partial_effects_on_outcome(
            covariates=covariate, values=values, cmap="coolwarm", y=type, ax=ax
        )

        # Add x and y labels
        ax.set_xlabel("Time", fontsize=13)
        if type == "survival_function":
            ax.set_ylabel("Survival Probability", fontsize=13)
        else:
            ax.set_ylabel("Cumulative Hazard", fontsize=13)

        # Add chart title
        ax.set_title(f"Partial Effects on Outcome of {covariate}", fontsize=14)

        # Remove background grid
        ax.grid(False)


    def plot_survival_curve(self, aft_model, data_point: pd.DataFrame):
        """Plots the survival function for individuals, given their covariates.

        Args:
            aft_model: An instance of a fitted AFT model (WeibullAFTFitter, LogNormalAFTFitter, or LogLogisticAFTFitter).
            data_point (pd.DataFrame): A Pandas DataFrame of covariates.
        """

        # Generate survival curve
        t = np.linspace(0, 1200, 100)
        pred = aft_model.predict_survival_function(data_point, times=t)

        # Plot survival curve
        plt.plot(t, pred.values)
        plt.xlabel("Time", fontsize=13)
        plt.ylabel("Survival Probability", fontsize=13)
        plt.title("Survival Function", fontsize=14)
        plt.show()

    def predict_aft_model(self, aft_model, n_time_periods: int):
        """Generates survival predictions for a specified number of time periods using an AFT model.

        Takes an AFT model and generates survival predictions for a specified number of time periods.

        Args:
            aft_model: An instance of a fitted AFT model (WeibullAFTFitter, LogNormalAFTFitter, or LogLogisticAFTFitter).
            n_time_periods (int): The number of time periods for which predictions should be generated.

        Returns:
            pd.DataFrame: DataFrame containing survival predictions for each ID and time period.
        """

        # Remove primary key column
        survival_df = self.data.drop(columns=[self.primary_col])
        # Handle zero values in the duration column
        survival_df[self.duration_col] = survival_df[self.duration_col].replace(
            0, 0.0001
        )

        predictions_df_list = []

        for time_period in range(1, n_time_periods + 1):
            pred_data = pd.DataFrame(
                {"id": self.data[self.primary_col], "pred_period": time_period}
            )

            # Generate survival predictions
            predictions = aft_model.predict_survival_function(
                survival_df, times=[time_period]
            )
            surv_prob = round(1 - predictions, 5)

            # Convert predictions to a DataFrame
            predictions_df = pd.DataFrame(
                surv_prob.T.values, columns=["survival_probability"]
            )

            # Concatenate customer_id and time_period with predictions DataFrame
            result_df = pd.concat([pred_data, predictions_df], axis=1)

            # Append to the list
            predictions_df_list.append(result_df)

        # Concatenate all predictions into a single DataFrame
        predictions_df = pd.concat(predictions_df_list, ignore_index=True)
        print("Predictions generated successfully.")
        return predictions_df
