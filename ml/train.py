import os
import pickle

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from xgboost import XGBClassifier

from ml.preprocess import load_data, prepare_data
from ml.config import MODEL_PATH


from ml.config import DATA_PATH



def train_models():

    # -----------------------------
    # Load dataset
    # -----------------------------

    df = load_data(DATA_PATH)

    # -----------------------------
    # Prepare data
    # -----------------------------

    X_train, X_test, y_train, y_test = prepare_data(df)

    # -----------------------------
    # Random Forest
    # -----------------------------

    rf_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=15,
        random_state=42,
        class_weight="balanced"
    )

    rf_model.fit(X_train, y_train)

    rf_predictions = rf_model.predict(X_test)

    rf_accuracy = accuracy_score(
        y_test,
        rf_predictions
    )

    print("Random Forest Accuracy:",
          round(rf_accuracy * 100, 2), "%")

    # -----------------------------
    # XGBoost
    # -----------------------------

    xgb_model = XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        eval_metric="logloss"
    )

    xgb_model.fit(X_train, y_train)

    xgb_predictions = xgb_model.predict(X_test)

    xgb_accuracy = accuracy_score(
        y_test,
        xgb_predictions
    )

    print("XGBoost Accuracy:",
          round(xgb_accuracy * 100, 2), "%")

    # -----------------------------
    # Select best model
    # -----------------------------

    if xgb_accuracy >= rf_accuracy:

        best_model = xgb_model
        best_name = "XGBoost"
        best_accuracy = xgb_accuracy

    else:

        best_model = rf_model
        best_name = "Random Forest"
        best_accuracy = rf_accuracy

    print("\nBest Model:", best_name)
    print(
        "Best Accuracy:",
        round(best_accuracy * 100, 2),
        "%"
    )

    # -----------------------------
    # Create model directory
    # -----------------------------

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)

    # -----------------------------
    # Save model
    # -----------------------------

    with open(MODEL_PATH, "wb") as file:

        pickle.dump(best_model, file)

    print("\nModel saved at:")
    print(MODEL_PATH)


if __name__ == "__main__":

    train_models()