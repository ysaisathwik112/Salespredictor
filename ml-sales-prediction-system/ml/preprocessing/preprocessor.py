"""
Data Preprocessor
Handles feature engineering, scaling, and encoding for the sales prediction model.
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline


# Feature definitions
NUMERICAL_FEATURES = [
    "item_weight",
    "item_visibility",
    "item_mrp",
    "outlet_establishment_year",
]

CATEGORICAL_FEATURES = [
    "item_type",
    "outlet_size",
    "outlet_location_type",
    "outlet_type",
]

TARGET_COLUMN = "item_outlet_sales"


def create_preprocessor():
    """Create a preprocessing pipeline for the sales data."""
    numerical_transformer = StandardScaler()
    categorical_transformer = OneHotEncoder(handle_unknown="ignore", sparse_output=True)

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )

    return preprocessor


def engineer_features(df):
    """Apply feature engineering to the raw dataframe."""
    df = df.copy()

    # Fill missing item weights with median
    if "item_weight" in df.columns:
        df["item_weight"] = df["item_weight"].fillna(df["item_weight"].median())

    # Fill missing outlet sizes with mode
    if "outlet_size" in df.columns:
        df["outlet_size"] = df["outlet_size"].fillna(df["outlet_size"].mode()[0])

    # Clip visibility to reasonable range
    if "item_visibility" in df.columns:
        df["item_visibility"] = df["item_visibility"].clip(lower=0.0, upper=0.35)

    # Ensure MRP is positive
    if "item_mrp" in df.columns:
        df["item_mrp"] = df["item_mrp"].clip(lower=10.0)

    return df


def generate_synthetic_data(n_samples=5000, random_state=42):
    """
    Generate synthetic sales data for training the model.
    Simulates realistic retail sales patterns.
    """
    np.random.seed(random_state)

    item_types = [
        "Dairy", "Soft Drinks", "Meat", "Fruits and Vegetables",
        "Household", "Baking Goods", "Snack Foods", "Frozen Foods",
        "Breakfast", "Health and Hygiene", "Hard Drinks", "Canned",
        "Breads", "Starchy Foods", "Others", "Seafood",
    ]

    outlet_sizes = ["Small", "Medium", "High"]
    outlet_location_types = ["Tier 1", "Tier 2", "Tier 3"]
    outlet_types = [
        "Grocery Store", "Supermarket Type1",
        "Supermarket Type2", "Supermarket Type3",
    ]

    data = {
        "item_weight": np.random.uniform(4.0, 22.0, n_samples),
        "item_visibility": np.random.uniform(0.0, 0.3, n_samples),
        "item_mrp": np.random.uniform(50.0, 10000.0, n_samples),
        "item_type": np.random.choice(item_types, n_samples),
        "outlet_size": np.random.choice(outlet_sizes, n_samples, p=[0.3, 0.45, 0.25]),
        "outlet_location_type": np.random.choice(outlet_location_types, n_samples, p=[0.35, 0.35, 0.30]),
        "outlet_type": np.random.choice(outlet_types, n_samples, p=[0.25, 0.40, 0.20, 0.15]),
        "outlet_establishment_year": np.random.choice(
            range(1985, 2020), n_samples
        ),
    }

    df = pd.DataFrame(data)

    # Generate realistic sales based on features
    base_sales = 50000.0
    mrp_effect = df["item_mrp"] * np.random.uniform(8.0, 15.0, n_samples)
    visibility_effect = df["item_visibility"] * np.random.uniform(-50000, 20000, n_samples)

    # Outlet type effects
    outlet_multiplier = df["outlet_type"].map({
        "Grocery Store": 0.6,
        "Supermarket Type1": 1.0,
        "Supermarket Type2": 1.3,
        "Supermarket Type3": 1.5,
    })

    # Location effects
    location_multiplier = df["outlet_location_type"].map({
        "Tier 1": 1.2,
        "Tier 2": 1.0,
        "Tier 3": 0.8,
    })

    # Size effects
    size_multiplier = df["outlet_size"].map({
        "Small": 0.7,
        "Medium": 1.0,
        "High": 1.3,
    })

    # Item type effects
    type_multiplier = df["item_type"].map({
        "Dairy": 1.1, "Soft Drinks": 0.9, "Meat": 1.3,
        "Fruits and Vegetables": 1.0, "Household": 1.2,
        "Baking Goods": 0.8, "Snack Foods": 1.1,
        "Frozen Foods": 0.95, "Breakfast": 1.05,
        "Health and Hygiene": 1.15, "Hard Drinks": 0.85,
        "Canned": 0.9, "Breads": 0.75, "Starchy Foods": 0.8,
        "Others": 0.7, "Seafood": 1.25,
    })

    # Age effect (newer outlets sell more)
    age_effect = (2025 - df["outlet_establishment_year"]) * np.random.uniform(-5, 2, n_samples)

    # Calculate sales
    sales = (
        base_sales
        + mrp_effect
        + visibility_effect
        + age_effect
    ) * outlet_multiplier * location_multiplier * size_multiplier * type_multiplier

    # Add noise
    noise = np.random.normal(0, 20000, n_samples)
    sales = sales + noise

    # Ensure non-negative
    df["item_outlet_sales"] = np.maximum(sales, 50.0)

    return df
