import pandas as pd
from sklearn.model_selection import train_test_split
from ml.config import FEATURES, TARGET


def load_data(file_path):

    df = pd.read_csv(file_path)

    print("Dataset shape:", df.shape)

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Remove rows containing missing values
    df = df.dropna()

    return df


def prepare_data(df):

    X = df[FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    return X_train, X_test, y_train, y_test