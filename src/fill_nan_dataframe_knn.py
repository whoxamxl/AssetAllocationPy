from sklearn.impute import KNNImputer
import pandas as pd

def fill_nan_dataframe_knn(returns_dataframe):
    # Identify columns that are entirely NaN
    nan_columns = returns_dataframe.columns[returns_dataframe.isnull().all()].tolist()

    # Check if there are any such columns and raise an error with their names
    if nan_columns:
        raise ValueError(f"Columns entirely NaN: {', '.join(nan_columns)}")

    # Initialize the KNN Imputer
    imputer = KNNImputer(n_neighbors=5)

    # Impute the missing values
    returns_filled = imputer.fit_transform(returns_dataframe)

    # Convert the filled array back to a DataFrame
    returns_filled_df = pd.DataFrame(returns_filled, columns=returns_dataframe.columns,
                                     index=returns_dataframe.index)

    return returns_filled_df