"""
Pydantic schemas for data validation and serialization.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from uuid import uuid4


class ProductInput(BaseModel):
    """Input schema for product placement request."""

    product_name: str = Field(..., min_length=1, description="Name of the product")
    category: str = Field(..., min_length=1, description="Product category (e.g., Beverages, Snacks)")
    price: float = Field(..., gt=0, description="Product price in dollars")
    budget: float = Field(..., gt=0, description="Available placement budget in dollars")
    target_sales: int = Field(..., gt=0, description="Target units to sell")
    target_customers: str = Field(..., min_length=1, description="Target customer segment")
    expected_roi: float = Field(..., gt=0, description="Business owner's expected ROI")

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Validate and normalize category."""
        valid_categories = ['beverages', 'snacks', 'dairy', 'bakery', 'personal care']
        v_lower = v.lower()
        if v_lower not in valid_categories:
            # Allow it but warn
            pass
        return v.title()

    class Config:
        json_schema_extra = {
            "example": {
                "product_name": "Premium Energy Drink",
                "category": "Beverages",
                "price": 2.99,
                "budget": 5000.0,
                "target_sales": 1000,
                "target_customers": "Young adults 18-35, fitness enthusiasts",
                "expected_roi": 1.5
            }
        }


class ShelfLocation(BaseModel):
    """Schema for shelf location data."""

    shelf_id: str
    name: str
    zone: str  # endcap, eye_level, low_shelf, checkout
    traffic_index: float
    visibility_factor: float
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    notes: Optional[str] = None


class ROIPrediction(BaseModel):
    """Schema for ROI prediction result."""

    location: str
    roi: float = Field(..., description="Predicted ROI score")
    confidence_interval: Tuple[float, float] = Field(..., description="80% confidence interval")
    placement_cost: float = Field(..., description="Estimated placement cost")
    confidence_level: float = Field(default=0.80, description="Confidence level (0-1)")


class FeatureImportance(BaseModel):
    """Schema for SHAP-style feature importance."""

    feature: str
    shap_value: float
    feature_value: float


class HistoricalExample(BaseModel):
    """Schema for historical product example."""

    product_name: str
    category: str
    actual_roi: float
    placement_date: str
    similarity: Optional[float] = None


class CompetitorProduct(BaseModel):
    """Schema for competitor product."""

    product_name: str
    price: float
    observed_roi: float
    market_share: Optional[float] = None


class Explanation(BaseModel):
    """Schema for comprehensive explanation."""

    location: str
    roi_score: float
    feature_importance: str  # Markdown formatted
    historical_evidence: str  # Markdown formatted
    competitor_benchmark: str  # Markdown formatted
    counterfactual: str  # Markdown formatted
    confidence_assessment: Optional[str] = None


class Recommendation(BaseModel):
    """Schema for final recommendation."""

    recommendations: Dict[str, float] = Field(..., description="Location -> ROI mapping")
    explanation: Explanation
    session_id: str
    timestamp: datetime


class PlacementState(BaseModel):
    """State object that flows through all agents."""

    # Core product information
    product: ProductInput

    # Session metadata
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)

    # Agent outputs (optional, populated as workflow progresses)
    locations: Optional[List[ShelfLocation]] = None
    roi_predictions: Optional[Dict[str, ROIPrediction]] = None
    feature_importance: Optional[Dict[str, List[FeatureImportance]]] = None
    historical_examples: Optional[Dict[str, List[HistoricalExample]]] = None
    competitors: Optional[Dict[str, List[CompetitorProduct]]] = None
    final_recommendations: Optional[Dict[str, float]] = None
    explanation: Optional[Explanation] = None

    # Error tracking
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
