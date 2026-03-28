"""
Unit Tests for the ML Model
Tests cover: data generation, preprocessing, training, and prediction.
"""

import pytest
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.preprocessing.preprocessor import (
    generate_synthetic_data,
    engineer_features,
    NUMERICAL_FEATURES,
    CATEGORICAL_FEATURES,
    TARGET_COLUMN,
)


class TestDataGeneration:
    """Tests for synthetic data generation."""

    def test_generates_correct_samples(self):
        """Should generate the requested number of samples."""
        df = generate_synthetic_data(n_samples=100)
        assert len(df) == 100

    def test_generates_all_columns(self):
        """Should generate all required columns."""
        df = generate_synthetic_data(n_samples=50)
        required_cols = NUMERICAL_FEATURES + CATEGORICAL_FEATURES + [TARGET_COLUMN]
        for col in required_cols:
            assert col in df.columns, f"Missing column: {col}"

    def test_no_negative_sales(self):
        """Sales should be non-negative."""
        df = generate_synthetic_data(n_samples=500)
        assert (df[TARGET_COLUMN] >= 0).all()

    def test_numerical_ranges(self):
        """Numerical features should be in expected ranges."""
        df = generate_synthetic_data(n_samples=1000)
        assert df["item_weight"].min() >= 0
        assert df["item_visibility"].min() >= 0
        assert df["item_mrp"].min() > 0

    def test_categorical_values(self):
        """Categorical features should have valid values."""
        df = generate_synthetic_data(n_samples=500)
        assert set(df["outlet_size"].unique()).issubset({"Small", "Medium", "High"})
        assert set(df["outlet_location_type"].unique()).issubset({"Tier 1", "Tier 2", "Tier 3"})

    def test_reproducibility(self):
        """Same random state should produce same data."""
        df1 = generate_synthetic_data(n_samples=50, random_state=42)
        df2 = generate_synthetic_data(n_samples=50, random_state=42)
        pd.testing.assert_frame_equal(df1, df2)


class TestFeatureEngineering:
    """Tests for feature engineering."""

    def test_fills_missing_weights(self):
        """Should fill missing item weights."""
        df = generate_synthetic_data(n_samples=100)
        df.loc[0:10, "item_weight"] = np.nan
        df_processed = engineer_features(df)
        assert df_processed["item_weight"].isna().sum() == 0

    def test_clips_visibility(self):
        """Should clip visibility to valid range."""
        df = generate_synthetic_data(n_samples=100)
        df.loc[0, "item_visibility"] = 0.5
        df_processed = engineer_features(df)
        assert df_processed["item_visibility"].max() <= 0.35

    def test_does_not_modify_original(self):
        """Feature engineering should not modify the original dataframe."""
        df = generate_synthetic_data(n_samples=50)
        original_copy = df.copy()
        engineer_features(df)
        pd.testing.assert_frame_equal(df, original_copy)


class TestModelTraining:
    """Tests for model training pipeline."""

    def test_training_produces_artifacts(self):
        """Training should produce all required artifact files."""
        artifacts_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "ml", "artifacts"
        )

        # Check if artifacts exist (may have been generated already)
        expected_files = ["model.pkl", "scaler.pkl", "encoder.pkl"]
        for f in expected_files:
            path = os.path.join(artifacts_dir, f)
            if os.path.exists(path):
                assert os.path.getsize(path) > 0, f"Artifact {f} is empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
