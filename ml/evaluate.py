from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from ml.preprocess import load_data, prepare_data
from ml.config import MODEL_PATH

import pickle


DATA_PATH = "ml/data/flood_data.csv"


def evaluate_model():

    # Load data

    df = load_data(DATA_PATH)

    X_train, X_test, y_train, y_test = prepare_data(df)

    # Load trained model

    with open(MODEL_PATH, "rb") as file:

        model = pickle.load(file)

    # Predictions

    predictions = model.predict(X_test)

    # Metrics

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    print("\n========== MODEL EVALUATION ==========\n")

    print(
        "Accuracy :",
        round(accuracy * 100, 2),
        "%"
    )

    print(
        "Precision:",
        round(precision * 100, 2),
        "%"
    )

    print(
        "Recall   :",
        round(recall * 100, 2),
        "%"
    )

    print(
        "F1 Score :",
        round(f1 * 100, 2),
        "%"
    )

    print("\nClassification Report:\n")

    print(
        classification_report(
            y_test,
            predictions,
            zero_division=0
        )
    )

    print("Confusion Matrix:\n")

    print(
        confusion_matrix(
            y_test,
            predictions
        )
    )


if __name__ == "__main__":

    evaluate_model()