"""
Model Training Pipeline
End-to-end training script for the Sales Prediction model.
Generates synthetic data, preprocesses, trains, evaluates, and saves artifacts.
"""

import os
import sys
import json
import joblib
import numpy as np
import pandas as pd
from datetime import datetime, timezone
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, PROJECT_ROOT)

from ml.preprocessing.preprocessor import (
    generate_synthetic_data,
    engineer_features,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET_COLUMN,
)


def train_model(n_samples=5000, test_size=0.2, random_state=42):
    """
    Full training pipeline:
    1. Generate/load data
    2. Feature engineering
    3. Preprocessing (scale + encode)
    4. Train GradientBoosting model
    5. Evaluate
    6. Save artifacts
    """
    print("=" * 60)
    print("  Sales Prediction Model — Training Pipeline")
    print("=" * 60)

    # ── Step 1: Generate Data ──
    print("\n[1/6] Generating synthetic training data...")
    df = generate_synthetic_data(n_samples=n_samples, random_state=random_state)
    print(f"  → Generated {len(df)} samples with {len(df.columns)} features")

    # ── Step 2: Feature Engineering ──
    print("\n[2/6] Applying feature engineering...")
    df = engineer_features(df)
    print(f"  → Features: {NUMERICAL_FEATURES + CATEGORICAL_FEATURES}")

    # ── Step 3: Split Data ──
    print("\n[3/6] Splitting data...")
    X = df[NUMERICAL_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    print(f"  → Train: {len(X_train)}, Test: {len(X_test)}")

    # ── Step 4: Preprocessing ──
    print("\n[4/6] Fitting preprocessors...")

    # Fit scaler on numerical features
    scaler = StandardScaler()
    X_train_num = scaler.fit_transform(X_train[NUMERICAL_FEATURES])
    X_test_num = scaler.transform(X_test[NUMERICAL_FEATURES])

    # Fit encoder on categorical features
    encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=True)
    X_train_cat = encoder.fit_transform(X_train[CATEGORICAL_FEATURES])
    X_test_cat = encoder.transform(X_test[CATEGORICAL_FEATURES])

    # Combine
    X_train_processed = np.hstack([X_train_num, X_train_cat.toarray()])
    X_test_processed = np.hstack([X_test_num, X_test_cat.toarray()])

    # Build feature names list
    cat_feature_names = encoder.get_feature_names_out(CATEGORICAL_FEATURES).tolist()
    all_feature_names = NUMERICAL_FEATURES + cat_feature_names

    print(f"  → Total features after encoding: {len(all_feature_names)}")

    # ── Step 5: Train Model ──
    print("\n[5/6] Training GradientBoosting model...")
    model = GradientBoostingRegressor(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        min_samples_split=5,
        min_samples_leaf=3,
        subsample=0.85,
        random_state=random_state,
        loss="squared_error",
    )

    model.fit(X_train_processed, y_train)

    # Cross-validation
    cv_scores = cross_val_score(
        model, X_train_processed, y_train, cv=5, scoring="r2"
    )
    print(f"  → Cross-validation R2: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")

    # ── Step 6: Evaluate ──
    print("\n[6/6] Evaluating model...")
    y_pred_train = model.predict(X_train_processed)
    y_pred_test = model.predict(X_test_processed)

    # Training metrics
    train_r2 = r2_score(y_train, y_pred_train)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    train_mae = mean_absolute_error(y_train, y_pred_train)

    # Test metrics
    test_r2 = r2_score(y_test, y_pred_test)
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    test_mae = mean_absolute_error(y_test, y_pred_test)

    print(f"\n  {'Metric':<20} {'Train':>12} {'Test':>12}")
    print(f"  {'─' * 44}")
    print(f"  {'R2 Score':<20} {train_r2:>12.4f} {test_r2:>12.4f}")
    print(f"  {'RMSE':<20} {train_rmse:>12.2f} {test_rmse:>12.2f}")
    print(f"  {'MAE':<20} {train_mae:>12.2f} {test_mae:>12.2f}")

    # Feature importance
    print("\n  Top 10 Feature Importances:")
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1][:10]
    for i, idx in enumerate(indices):
        name = all_feature_names[idx] if idx < len(all_feature_names) else f"feature_{idx}"
        print(f"    {i + 1:2d}. {name:<35} {importances[idx]:.4f}")

    # ── Save Artifacts ──
    artifacts_dir = os.path.join(PROJECT_ROOT, "ml", "artifacts")
    os.makedirs(artifacts_dir, exist_ok=True)

    model_path = os.path.join(artifacts_dir, "model.pkl")
    scaler_path = os.path.join(artifacts_dir, "scaler.pkl")
    encoder_path = os.path.join(artifacts_dir, "encoder.pkl")
    feature_names_path = os.path.join(artifacts_dir, "feature_names.pkl")
    metadata_path = os.path.join(artifacts_dir, "training_metadata.json")

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)
    joblib.dump(encoder, encoder_path)
    joblib.dump(all_feature_names, feature_names_path)

    # Save metadata
    metadata = {
        "version": "1.0.0",
        "algorithm": "GradientBoostingRegressor",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "n_features": len(all_feature_names),
        "hyperparameters": {
            "n_estimators": 200,
            "max_depth": 6,
            "learning_rate": 0.1,
            "min_samples_split": 5,
            "min_samples_leaf": 3,
            "subsample": 0.85,
        },
        "metrics": {
            "train": {"r2": train_r2, "rmse": train_rmse, "mae": train_mae},
            "test": {"r2": test_r2, "rmse": test_rmse, "mae": test_mae},
            "cv_r2_mean": float(cv_scores.mean()),
            "cv_r2_std": float(cv_scores.std()),
        },
    }

    with open(metadata_path, "w") as f:
        json.dump(metadata, f, indent=2, default=str)

    print(f"\n  Artifacts saved to: {artifacts_dir}")
    print(f"    → model.pkl ({os.path.getsize(model_path) / 1024:.1f} KB)")
    print(f"    → scaler.pkl ({os.path.getsize(scaler_path) / 1024:.1f} KB)")
    print(f"    → encoder.pkl ({os.path.getsize(encoder_path) / 1024:.1f} KB)")
    print(f"    → feature_names.pkl")
    print(f"    → training_metadata.json")

    # Print for API parsing
    print(f"\nR2 Score: {test_r2:.4f}")
    print(f"RMSE: {test_rmse:.2f}")
    print(f"MAE: {test_mae:.2f}")

    print("\n" + "=" * 60)
    print("  Training completed successfully!")
    print("=" * 60)

    return model, scaler, encoder, metadata


if __name__ == "__main__":
    train_model()
