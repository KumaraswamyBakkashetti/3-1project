# Trainer/xgb_trainer.py
import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import mean_squared_error, r2_score
import joblib
import xgboost as xgb

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CSV_PATH = os.path.join(ROOT, "data", "features.csv")
MODEL_DIR = os.path.join(ROOT, "models")
os.makedirs(MODEL_DIR, exist_ok=True)


def train_xgb(csv_path=CSV_PATH, model_out=os.path.join(MODEL_DIR, "xgb_model.joblib")):
    if not os.path.exists(csv_path):
        print("No features.csv found at", csv_path)
        return

    df = pd.read_csv(csv_path)
    if "collective_score" not in df.columns:
        print("collective_score not found in features.csv — cannot train.")
        return

    # Drop rows with missing target
    df = df.dropna(subset=["collective_score"])
    if df.shape[0] < 10:
        print("Not enough rows to train (need >= 10). Rows:", df.shape[0])
        return

    # Use all numeric columns except the target as features
    X = df.select_dtypes(include=[np.number]).drop(columns=["collective_score"], errors=True)
    y = df["collective_score"].astype(float)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = xgb.XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    r2 = r2_score(y_test, preds)
    print(f"Trained XGB. Test MSE: {mse:.4f}, R2: {r2:.4f}")

    joblib.dump({"model": model, "columns": X.columns.tolist()}, model_out)
    print("Model saved to", model_out)


if __name__ == "__main__":
    train_xgb()
