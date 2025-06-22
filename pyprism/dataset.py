import sklearn
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import KBinsDiscretizer
import pandas as pd
from sklearn.model_selection import train_test_split


def add_missing(df: pd.DataFrame, p: float) -> pd.DataFrame:
    """
  Introduces missing data into a pandas DataFrame with a given probability.

  Args:
    df: The input DataFrame.
    p: The probability of a cell being set to NaN (between 0 and 1).

  Returns:
    A new DataFrame with missing values.
  """
    if not 0 <= p <= 1:
        raise ValueError("Probability 'p' must be between 0 and 1.")

    # Create a boolean mask where True indicates a cell to be set to NaN
    mask = np.random.choice([True, False], size=df.shape, p=[p, 1 - p])

    # Create a copy to avoid modifying the original DataFrame
    df_missing = df.copy()

    # Apply the mask to set values to NaN
    df_missing[mask] = np.nan

    return df_missing


def discretize(X, thresh_uniq=10, disc_bins=10):
    # Create a copy to store discretized data
    X_discretized = X.copy()

    # Identify columns that are already discrete (assuming less than thresh_uniq unique values)
    discrete_cols = [
        col
        for col in X.columns
        if X[col].nunique() < thresh_uniq and X[col].dtype != "object"
    ]

    # Discretize continuous columns
    continuous_cols = [col for col in X.columns if col not in discrete_cols]
    discretizers = {}
    for col in continuous_cols:
        # Handle NaN values by temporarily dropping them for discretization
        col_data = X[col].dropna()
        if not col_data.empty:
            # Use KBinsDiscretizer to discretize based on quantiles (percentiles)
            # strategy='quantile' ensures equal number of samples in each bin
            # n_bins=10 for 10 discrete levels
            discretizer = KBinsDiscretizer(
                n_bins=disc_bins, encode="ordinal", strategy="quantile"
            )
            discretizers[col] = discretizer
            # Fit and transform the non-NaN data
            discretized_data = discretizer.fit_transform(col_data.values.reshape(-1, 1))
            # Create a pandas Series with the same index as the original non-NaN data
            discretized_series = pd.Series(
                discretized_data.flatten(), index=col_data.index
            )
            # Update the discretized dataframe with the results, keeping NaNs in their original positions
            X_discretized[col] = discretized_series

    # Ensure discrete columns are included in the final discretized dataframe without modification
    for col in discrete_cols:
        X_discretized[col] = X[col]

    return X_discretized, discretizers


def discretize_y(y, thresh_uniq=10, disc_bins=10):
    # Discretize y using KBinsDiscretizer based on quantiles
    # Handle NaN values by temporarily dropping them for discretization
    y_data = y.dropna()
    if y_data.nunique() > thresh_uniq:
        if not y_data.empty:
            # Use KBinsDiscretizer to discretize based on quantiles (percentiles)
            discretizer_y = KBinsDiscretizer(
                n_bins=disc_bins, encode="ordinal", strategy="quantile"
            )
            # Fit and transform the non-NaN data
            discretized_y_data = discretizer_y.fit_transform(
                y_data.values.reshape(-1, 1)
            )
            # Create a pandas Series with the same index as the original non-NaN data
            y_discretized = pd.Series(discretized_y_data.flatten(), index=y_data.index)
        else:
            y_discretized = pd.Series(
                dtype=float
            )  # Create an empty series if y_data was empty
    else:
        return y_data, None
    return y_discretized, discretizer_y


def plot_discretization(
    X: pd.DataFrame, hist_bins: int = 100, disc_bins: int = 10, title: str = None
):
    # Discretize variables based on percentiles and add vertical lines
    for col in X.columns:
        # Calculate the 10th percentile boundaries
        percentiles = np.percentile(
            X[col].dropna(), np.arange(0, 101, 100 // disc_bins)
        )

        plt.figure(figsize=(8, 6))
        plt.hist(X[col], bins=hist_bins)
        if title is None:
            plt.title(f"Histogram of {col}")
        else:
            plt.title(f"{title}")
        plt.xlabel(col)
        plt.ylabel("Frequency")
        # Add vertical lines at percentile boundaries
        for p in percentiles:
            plt.axvline(p, color="red", linestyle="dashed", linewidth=1)
        plt.show()


def plot_discretized_data(X_discretized: pd.DataFrame, title: str = None):
    # Create histograms for the discretized variables
    for col in X_discretized.columns:
        plt.figure(figsize=(8, 6))
        X_discretized[col].value_counts().sort_index().plot(kind="bar")
        if title is None:
            plt.title(f"Histogram of {col}")
        else:
            plt.title(f"{title}")
        plt.xlabel(col)
        plt.ylabel("Frequency")
        plt.show()


def to_dat(
    X_discretized: pd.DataFrame,
    y_discretized: pd.DataFrame,
    out_filename: str = "output.dat",
    pred: str = "data",
    with_y=True,
):
    data = []
    # Ensure both X_discretized and y_discretized have the same index for alignment
    # If y_discretized might have missing indices compared to X_discretized,
    # we need to align them. Let's use the index of X_discretized as the base.
    aligned_y = y_discretized.reindex(X_discretized.index)

    for index, row in X_discretized.iterrows():
        # Convert row to list and handle NaN
        row_list = [str(int(x)) if pd.notna(x) else "_" for x in row.tolist()]

        # Get the corresponding y value, handling NaN
        y_value = (
            aligned_y.loc[index]
            if index in aligned_y.index and pd.notna(aligned_y.loc[index])
            else "_"
        )
        if y_value != "_":
            y_value = str(int(y_value))

        # Combine the row list and the y value
        data.append((row_list, y_value))

    # Write to dat file
    with open(out_filename, "w") as fp:
        for row, y_value in data:
            if with_y:
                fp.write(pred + "(" + y_value + ",[" + ",".join(row) + "]).\n")
            else:
                fp.write(pred + "([" + ",".join(row) + "]).\n")


def apply_discretizer(X, discretizers, thresh_uniq=10):
    """Apply fitted discretizers to X."""
    X_discretized = X.copy()
    for col, discretizer in discretizers.items():
        col_data = X[col]
        if col_data.isnull().all():
            continue
        transformed = discretizer.transform(col_data.values.reshape(-1, 1))
        X_discretized[col] = pd.Series(transformed.flatten(), index=X.index)

    # Keep any discrete columns unchanged
    for col in X.columns:
        if col not in discretizers:
            X_discretized[col] = X[col]

    return X_discretized


def preprocess(
    X,
    y,
    missing_px: float = 0.0,  # Probability of introducing missing values in features X (0.0 to 1.0)
    missing_py: float = 0.0,  # Probability of introducing missing values in target y (0.0 to 1.0)
    disc_bins_x: int = 5,  # Number of bins used to discretize each feature column in X
    disc_bins_y: int = 8,  # Number of bins used to discretize the target y
    thresh_uniq_x: int = 10,  # Threshold for number of unique values in a column of X before discretizing
    thresh_uniq_y: int = 10,  # Threshold for number of unique values in y before discretizing
    out_filename=None,
    out_test_filename=None,
    pred="data",
    with_y=True,
    test_ratio=0.0,
):  # Returns: discretized X, y, and list of feature names
    if missing_px > 0:
        X = add_missing(X, p=missing_px)
    if missing_py > 0:
        y = add_missing(y, p=missing_py)
    if test_ratio > 0:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_ratio, random_state=42
        )

        X_discretized, discretizers = discretize(
            X_train, thresh_uniq=thresh_uniq_x, disc_bins=disc_bins_x
        )
        y_discretized, discretizer_y = discretize_y(
            y_train, thresh_uniq=thresh_uniq_y, disc_bins=disc_bins_y
        )

        # Apply the same discretizers to test data
        X_test_disc = apply_discretizer(X_test, discretizers, thresh_uniq=thresh_uniq_x)
        if discretizer_y is not None:
            y_test_disc = pd.Series(
                discretizer_y.transform(y_test.values.reshape(-1, 1)).flatten(),
                index=y_test.index,
            )
        else:
            y_test_disc = y_test
    else:
        X_discretized, discretizers = discretize(
            X, thresh_uniq=thresh_uniq_x, disc_bins=disc_bins_x
        )
        y_discretized, discretizer_y = discretize_y(
            y, thresh_uniq=thresh_uniq_y, disc_bins=disc_bins_y
        )
        X_test_disc = None
        y_test_disc = None

    if out_filename is not None:
        to_dat(X_discretized, y_discretized, out_filename, pred=pred, with_y=with_y)
    if out_test_filename is not None and X_test_disc is not None:
        to_dat(X_test_disc, y_test_disc, out_test_filename, pred=pred, with_y=with_y)
    attr_list = X_discretized.columns
    out = {
        "X": X,
        "y": y,
        "X_discretized": X_discretized,
        "y_discretized": y_discretized,
        "X_test_discretized": X_test_disc,
        "y_test_discretized": y_test_disc,
        "X_discretizers": discretizers,
        "y_discretizer": discretizer_y,
        "attr_list": attr_list,
    }
    return out


def load_discrete_diabetes(
    missing_px: float = 0.0,  # Probability of introducing missing values in features X (0.0 to 1.0)
    missing_py: float = 0.0,  # Probability of introducing missing values in target y (0.0 to 1.0)
    disc_bins_x: int = 5,  # Number of bins used to discretize each feature column in X
    disc_bins_y: int = 8,  # Number of bins used to discretize the target y
    thresh_uniq_x: int = 10,  # Threshold for number of unique values in a column of X before discretizing
    thresh_uniq_y: int = 10,  # Threshold for number of unique values in y before discretizing
    out_filename=None,
    out_test_filename=None,
    pred="data",
    with_y=True,
    test_ratio=0.0,
):  # Returns: discretized X, y, and list of feature names
    """
    This function loads the diabetes dataset, applies missing values if specified,
# and discretizes both features (X) and target (y).

    """
    X, y = sklearn.datasets.load_diabetes(return_X_y=True, as_frame=True, scaled=False)
    return preprocess(
        X,
        y,
        missing_px,
        missing_py,
        disc_bins_x,
        disc_bins_y,
        thresh_uniq_x,
        thresh_uniq_y,
        out_filename=out_filename,
        out_test_filename=out_test_filename,
        pred=pred,
        with_y=with_y,
        test_ratio=test_ratio,
    )


def load_discrete_california_housing(
    missing_px: float = 0.0,  # Probability of introducing missing values in features X (0.0 to 1.0)
    missing_py: float = 0.0,  # Probability of introducing missing values in target y (0.0 to 1.0)
    disc_bins_x: int = 5,  # Number of bins used to discretize each feature column in X
    disc_bins_y: int = 8,  # Number of bins used to discretize the target y
    thresh_uniq_x: int = 10,  # Threshold for number of unique values in a column of X before discretizing
    thresh_uniq_y: int = 10,  # Threshold for number of unique values in y before discretizing
    out_filename=None,
    out_test_filename=None,
    pred="data",
    with_y=True,
    test_ratio=0.0,
):  # Returns: discretized X, y, and list of feature names
    """
    This function loads the diabetes dataset, applies missing values if specified,
# and discretizes both features (X) and target (y).

    """
    X, y = sklearn.datasets.fetch_california_housing(return_X_y=True, as_frame=True)
    return preprocess(
        X,
        y,
        missing_px,
        missing_py,
        disc_bins_x,
        disc_bins_y,
        thresh_uniq_x,
        thresh_uniq_y,
        out_filename=out_filename,
        out_test_filename=out_test_filename,
        pred=pred,
        with_y=with_y,
        test_ratio=test_ratio,
    )
