# Trainer/predict_mas.py
"""
Predict MAS_score for new MAS variants using trained XGBoost model
"""

import os
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
from pathlib import Path


def load_mas_model(model_path, metadata_path):
    """Load trained MAS predictor model"""
    model = xgb.XGBRegressor()
    model.load_model(model_path)
    
    metadata = joblib.load(metadata_path)
    feature_names = metadata['feature_names']
    
    print(f"[INFO] Loaded model: {model_path}")
    print(f"[INFO] Features: {len(feature_names)}")
    
    return model, feature_names


def predict_mas_score(model, feature_names, features_dict):
    """
    Predict MAS_score for a new MAS variant
    
    Args:
        model: Trained XGBoost model
        feature_names: List of feature names
        features_dict: Dictionary of feature values
    
    Returns:
        Predicted MAS_score (0-1)
    """
    # Create feature vector in correct order
    feature_vector = []
    for feat_name in feature_names:
        if feat_name not in features_dict:
            raise ValueError(f"Missing feature: {feat_name}")
        feature_vector.append(features_dict[feat_name])
    
    # Predict
    X = np.array(feature_vector).reshape(1, -1)
    mas_score = model.predict(X)[0]
    
    return float(mas_score)


def predict_from_csv(model, feature_names, csv_path):
    """Predict MAS_score for all MAS variants in a CSV file"""
    df = pd.read_csv(csv_path)
    print(f"\n[INFO] Predicting for {len(df)} MAS variants from {csv_path}")
    
    predictions = []
    for idx, row in df.iterrows():
        features_dict = row.to_dict()
        try:
            mas_score = predict_mas_score(model, feature_names, features_dict)
            predictions.append(mas_score)
        except Exception as e:
            print(f"[WARNING] Failed to predict for row {idx}: {e}")
            predictions.append(None)
    
    df['predicted_MAS_score'] = predictions
    
    # Compare with actual if available
    if 'MAS_score' in df.columns:
        df['prediction_error'] = abs(df['MAS_score'] - df['predicted_MAS_score'])
        print("\nPrediction vs Actual:")
        print(df[['mas_variant', 'MAS_score', 'predicted_MAS_score', 'prediction_error']].head(10))
        print(f"\nMean Absolute Error: {df['prediction_error'].mean():.4f}")
    else:
        print("\nPredictions:")
        print(df[['mas_variant', 'predicted_MAS_score']].head(10))
    
    return df


def main():
    """Main prediction pipeline"""
    base_dir = Path(__file__).parent.parent
    
    # Load model
    model_path = base_dir / 'models' / 'xgb_mas_model.json'
    metadata_path = base_dir / 'models' / 'xgb_mas_model_metadata.pkl'
    
    if not model_path.exists():
        print(f"[ERROR] Model not found: {model_path}")
        print("Train model first: python Trainer/xgb_trainer_mas.py")
        return
    
    model, feature_names = load_mas_model(str(model_path), str(metadata_path))
    
    # Example: Predict for a new MAS variant
    print("\n" + "=" * 60)
    print("Example: Predict MAS_score for CodeMAS_Optimized")
    print("=" * 60)
    
    example_features = {
        'avg_personal_score': 0.75,
        'max_personal_score': 0.92,
        'min_personal_score': 0.45,
        'total_latency_sec': 45.3,
        'avg_token_count': 67,
        'max_loops': 1.2,
        'avg_loops': 0.8,
        'num_nodes': 5,
        'num_edges': 4,
        'avg_degree': 1.6,
        'clustering_coefficient': 0.0,
        'transitivity': 0,
        'avg_betweenness_centrality': 0.167,
        'avg_closeness_centrality': 0.5,
        'pagerank_entropy': 1.61,
        'authority_entropy': 0.0,
        'density': 0.2,
        'diameter': 4
    }
    
    try:
        predicted_score = predict_mas_score(model, feature_names, example_features)
        print(f"\nPredicted MAS_score: {predicted_score:.4f}")
        
        # Interpret score
        if predicted_score >= 0.7:
            quality = "Excellent"
        elif predicted_score >= 0.5:
            quality = "Good"
        elif predicted_score >= 0.3:
            quality = "Fair"
        else:
            quality = "Poor"
        
        print(f"Quality Assessment: {quality}")
    except Exception as e:
        print(f"[ERROR] Prediction failed: {e}")
    
    # Predict for CSV file if available
    csv_path = base_dir / 'data' / 'mas_features_combined.csv'
    if csv_path.exists():
        print("\n" + "=" * 60)
        print("Predicting for all MAS variants in dataset")
        print("=" * 60)
        df_with_predictions = predict_from_csv(model, feature_names, str(csv_path))
        
        # Save predictions
        output_path = base_dir / 'data' / 'mas_predictions.csv'
        df_with_predictions.to_csv(output_path, index=False)
        print(f"\n[SAVED] Predictions to: {output_path}")


if __name__ == "__main__":
    main()
