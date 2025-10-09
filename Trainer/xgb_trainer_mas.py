# Trainer/xgb_trainer_mas.py
"""
XGBoost trainer for MAS-level predictions

Trains on aggregated MAS variant data instead of individual prompts.
Target variable: MAS_score (computed from benchmark scores via weak supervision)
"""

import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import xgboost as xgb
import joblib
from pathlib import Path


def load_mas_data(csv_path):
    """
    Load MAS-level aggregated data
    
    Args:
        csv_path: Path to mas_features.csv or mas_features_combined.csv
    
    Returns:
        X (features), y (MAS_score), feature_names
    """
    df = pd.read_csv(csv_path)
    print(f"[INFO] Loaded {len(df)} MAS variants from {csv_path}")
    
    # Check for MAS_score column
    if 'MAS_score' not in df.columns:
        raise ValueError("MAS_score column not found. Run mas_level_aggregator.py first.")
    
    # Define feature columns (exclude target and metadata)
    exclude_cols = [
        'MAS_score',  # Target variable
        'mas_variant',  # Categorical label
        'num_prompts_aggregated',  # Metadata
        'collective_score',  # Old target (not used)
        'humaneval_score',  # Used to compute MAS_score
        'gsm8k_score',  # Used to compute MAS_score
        'mmlu_score'  # Used to compute MAS_score
    ]
    
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    X = df[feature_cols].values
    y = df['MAS_score'].values
    
    print(f"\n[INFO] Features: {len(feature_cols)}")
    print(f"Feature names: {feature_cols}")
    print(f"\n[INFO] Target: MAS_score")
    print(f"MAS_score range: {y.min():.3f} - {y.max():.3f}")
    print(f"MAS_score mean: {y.mean():.3f} ± {y.std():.3f}")
    
    return X, y, feature_cols, df


def train_xgboost_mas(X, y, feature_names, test_size=0.2, random_state=42):
    """
    Train XGBoost model on MAS-level data
    
    Args:
        X: Feature matrix
        y: MAS_score target
        feature_names: List of feature names
        test_size: Test split ratio
        random_state: Random seed
    
    Returns:
        Trained model, test scores
    """
    print("\n" + "=" * 60)
    print("Training XGBoost for MAS_score Prediction")
    print("=" * 60)
    
    # Check data size
    if len(X) < 5:
        print(f"[WARNING] Only {len(X)} samples. Results may not be reliable.")
        print("[SUGGESTION] Run mas_level_aggregator.py to simulate more MAS variants")
    
    # Split data
    if len(X) >= 10:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        print(f"\n[INFO] Train size: {len(X_train)}, Test size: {len(X_test)}")
    else:
        # Use all data for training if too small
        X_train, X_test, y_train, y_test = X, X, y, y
        print(f"\n[WARNING] Using all {len(X)} samples for both train and test")
    
    # Configure XGBoost
    model = xgb.XGBRegressor(
        n_estimators=100,
        max_depth=5,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='reg:squarederror',
        random_state=random_state,
        verbosity=0
    )
    
    # Train model
    print("\n[TRAINING] Fitting XGBoost model...")
    model.fit(X_train, y_train)
    
    # Predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Metrics
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    train_mae = mean_absolute_error(y_train, y_pred_train)
    test_mae = mean_absolute_error(y_test, y_pred_test)
    
    print("\n" + "=" * 60)
    print("Model Performance")
    print("=" * 60)
    print(f"\nTrain Metrics:")
    print(f"  R² Score: {train_r2:.4f}")
    print(f"  RMSE: {train_rmse:.4f}")
    print(f"  MAE: {train_mae:.4f}")
    
    print(f"\nTest Metrics:")
    print(f"  R² Score: {test_r2:.4f}")
    print(f"  RMSE: {test_rmse:.4f}")
    print(f"  MAE: {test_mae:.4f}")
    
    # Cross-validation (if enough data)
    if len(X) >= 10:
        print("\n[CV] Running 5-fold cross-validation...")
        kfold = KFold(n_splits=min(5, len(X)), shuffle=True, random_state=random_state)
        cv_scores = cross_val_score(
            model, X, y, cv=kfold, scoring='r2'
        )
        print(f"CV R² Scores: {cv_scores}")
        print(f"CV Mean R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    
    # Feature importance
    print("\n" + "=" * 60)
    print("Top 10 Most Important Features")
    print("=" * 60)
    importance = model.feature_importances_
    feature_importance = sorted(
        zip(feature_names, importance),
        key=lambda x: x[1],
        reverse=True
    )
    for i, (feat, imp) in enumerate(feature_importance[:10], 1):
        print(f"{i:2d}. {feat:30s} {imp:.4f}")
    
    return model, {
        'train_r2': train_r2,
        'test_r2': test_r2,
        'train_rmse': train_rmse,
        'test_rmse': test_rmse,
        'train_mae': train_mae,
        'test_mae': test_mae,
        'feature_importance': feature_importance
    }


def save_model(model, feature_names, save_path):
    """Save trained model and metadata"""
    # Save XGBoost model
    model_path = save_path.replace('.pkl', '.json')
    model.save_model(model_path)
    print(f"\n[SAVED] XGBoost model: {model_path}")
    
    # Save feature names
    metadata = {
        'feature_names': feature_names,
        'model_type': 'XGBoost_MAS_Predictor',
        'target': 'MAS_score',
        'n_features': len(feature_names)
    }
    metadata_path = save_path.replace('.json', '_metadata.pkl')
    joblib.dump(metadata, metadata_path)
    print(f"[SAVED] Metadata: {metadata_path}")


def main():
    """Main training pipeline"""
    # Paths
    base_dir = Path(__file__).parent.parent
    
    # Try combined data first, fall back to basic aggregation
    combined_csv = base_dir / 'data' / 'mas_features_combined.csv'
    simulated_csv = base_dir / 'data' / 'mas_features_simulated.csv'
    basic_csv = base_dir / 'data' / 'mas_features.csv'
    
    if combined_csv.exists():
        data_path = combined_csv
        print(f"[INFO] Using combined MAS data: {combined_csv}")
    elif simulated_csv.exists():
        data_path = simulated_csv
        print(f"[INFO] Using simulated MAS data: {simulated_csv}")
    elif basic_csv.exists():
        data_path = basic_csv
        print(f"[INFO] Using basic MAS data: {basic_csv}")
    else:
        print("[ERROR] No MAS-level data found!")
        print("Run: python Trainer/mas_level_aggregator.py")
        return
    
    # Load data
    X, y, feature_names, df = load_mas_data(str(data_path))
    
    # Train model
    model, metrics = train_xgboost_mas(X, y, feature_names)
    
    # Save model
    model_path = base_dir / 'models' / 'xgb_mas_model.json'
    os.makedirs(model_path.parent, exist_ok=True)
    save_model(model, feature_names, str(model_path))
    
    # Summary
    print("\n" + "=" * 60)
    print("Training Complete!")
    print("=" * 60)
    print(f"\nModel saved to: {model_path}")
    print(f"Test R² Score: {metrics['test_r2']:.4f}")
    print(f"Test RMSE: {metrics['test_rmse']:.4f}")
    
    print("\nNext steps:")
    print("1. Use Trainer/predict_mas.py to predict MAS_score for new variants")
    print("2. Generate more MAS variants for better model performance")
    print("3. Experiment with different MAS configurations")


if __name__ == "__main__":
    main()
