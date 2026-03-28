"""
Marshmallow Schemas for Input Validation
"""

from marshmallow import Schema, fields, validate, validates, ValidationError


VALID_ITEM_TYPES = [
    "Dairy", "Soft Drinks", "Meat", "Fruits and Vegetables",
    "Household", "Baking Goods", "Snack Foods", "Frozen Foods",
    "Breakfast", "Health and Hygiene", "Hard Drinks", "Canned",
    "Breads", "Starchy Foods", "Others", "Seafood",
]

VALID_OUTLET_SIZES = ["Small", "Medium", "High"]
VALID_OUTLET_LOCATION_TYPES = ["Tier 1", "Tier 2", "Tier 3"]
VALID_OUTLET_TYPES = [
    "Grocery Store", "Supermarket Type1",
    "Supermarket Type2", "Supermarket Type3",
]


class PredictionInputSchema(Schema):
    """Schema for validating prediction input data."""

    item_weight = fields.Float(
        required=True,
        validate=validate.Range(min=0.1, max=50.0),
        metadata={"description": "Weight of the item (0.1 - 50.0 kg)"},
    )
    item_visibility = fields.Float(
        required=True,
        validate=validate.Range(min=0.0, max=0.35),
        metadata={"description": "Display area percentage (0.0 - 0.35)"},
    )
    item_mrp = fields.Float(
        required=True,
        validate=validate.Range(min=10.0, max=20000.0),
        metadata={"description": "Maximum Retail Price (10.0 - 20000.0)"},
    )
    item_type = fields.String(
        required=True,
        validate=validate.OneOf(VALID_ITEM_TYPES),
        metadata={"description": "Category of the item"},
    )
    outlet_size = fields.String(
        required=True,
        validate=validate.OneOf(VALID_OUTLET_SIZES),
        metadata={"description": "Size of the outlet"},
    )
    outlet_location_type = fields.String(
        required=True,
        validate=validate.OneOf(VALID_OUTLET_LOCATION_TYPES),
        metadata={"description": "Location tier of the outlet"},
    )
    outlet_type = fields.String(
        required=True,
        validate=validate.OneOf(VALID_OUTLET_TYPES),
        metadata={"description": "Type of the outlet"},
    )
    outlet_establishment_year = fields.Integer(
        required=True,
        validate=validate.Range(min=1980, max=2025),
        metadata={"description": "Year the outlet was established"},
    )

    @validates("item_weight")
    def validate_item_weight(self, value):
        if value <= 0:
            raise ValidationError("Item weight must be positive.")


class BatchPredictionSchema(Schema):
    """Schema for batch prediction input."""
    predictions = fields.List(
        fields.Nested(PredictionInputSchema),
        required=True,
        validate=validate.Length(min=1, max=100),
        metadata={"description": "List of prediction inputs (max 100)"},
    )
