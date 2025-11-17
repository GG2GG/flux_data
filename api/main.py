"""
FastAPI Backend for Retail Product Placement Agent System
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import logging

# Import our agents and models
import sys
sys.path.append(str(Path(__file__).parent.parent))

from models.schemas import ProductInput, PlacementState
from workflows.orchestrator import Orchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Retail Product Placement Agent API",
    description="Multi-agent system for optimal product placement recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session store (in-memory for MVP, use Redis in production)
session_store: Dict[str, PlacementState] = {}

# Data store (loaded at startup)
data_store = {
    'products': [],
    'locations': [],
    'precomputed_roi': {},
    'feature_importance': {},
    'competitors': [],
    'historical_examples': []
}

# Initialize orchestrator
orchestrator = None


@app.on_event("startup")
async def startup_event():
    """Load data and initialize orchestrator on startup"""
    global orchestrator, data_store

    logger.info("🚀 Starting Retail Placement API...")

    # Load all precomputed data
    data_dir = Path(__file__).parent.parent / "data"

    try:
        # Load products
        with open(data_dir / "products.json", 'r') as f:
            data_store['products'] = json.load(f)
        logger.info(f"✅ Loaded {len(data_store['products'])} products")

        # Load locations
        with open(data_dir / "locations.json", 'r') as f:
            data_store['locations'] = json.load(f)
        logger.info(f"✅ Loaded {len(data_store['locations'])} locations")

        # Load precomputed ROI
        with open(data_dir / "precomputed_roi.json", 'r') as f:
            data_store['precomputed_roi'] = json.load(f)
        logger.info(f"✅ Loaded {len(data_store['precomputed_roi'])} ROI scores")

        # Load feature importance
        with open(data_dir / "feature_importance.json", 'r') as f:
            data_store['feature_importance'] = json.load(f)
        logger.info(f"✅ Loaded {len(data_store['feature_importance'])} feature importance scores")

        # Load competitors
        with open(data_dir / "competitors.json", 'r') as f:
            data_store['competitors'] = json.load(f)
        logger.info(f"✅ Loaded {len(data_store['competitors'])} competitor products")

        # Load historical examples
        with open(data_dir / "historical_examples.json", 'r') as f:
            data_store['historical_examples'] = json.load(f)
        logger.info(f"✅ Loaded {len(data_store['historical_examples'])} historical examples")

        # Initialize orchestrator with data
        orchestrator = Orchestrator(data_dir=str(data_dir))
        orchestrator.data_store = data_store  # Pass preloaded data

        logger.info("✅ Orchestrator initialized")
        logger.info("🎉 API ready to serve requests!")

    except Exception as e:
        logger.error(f"❌ Error loading data: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("👋 Shutting down API...")
    session_store.clear()


# API Models

class AnalyzeRequest(BaseModel):
    """Request model for analyze endpoint"""
    product_name: str = Field(..., description="Name of the product")
    category: str = Field(..., description="Product category (Beverages, Snacks, Dairy, Bakery, Personal Care)")
    price: float = Field(..., gt=0, description="Product price in dollars")
    budget: float = Field(..., gt=0, description="Available placement budget in dollars")
    target_sales: int = Field(..., gt=0, description="Target units to sell")
    target_customers: str = Field(..., description="Target customer segment description")
    expected_roi: float = Field(..., gt=0, description="Expected ROI (e.g., 1.5 = 150% return)")

    class Config:
        schema_extra = {
            "example": {
                "product_name": "Premium Energy Drink",
                "category": "Beverages",
                "price": 2.99,
                "budget": 5000.00,
                "target_sales": 1000,
                "target_customers": "Young adults 18-35, fitness enthusiasts",
                "expected_roi": 1.5
            }
        }


class AnalyzeResponse(BaseModel):
    """Response model for analyze endpoint"""
    recommendations: Dict[str, float] = Field(..., description="Location to ROI mapping (top 5)")
    explanation: Dict[str, Any] = Field(..., description="Detailed explanation of top recommendation")
    session_id: str = Field(..., description="Session ID for follow-up questions")
    timestamp: str = Field(..., description="Analysis timestamp")

    class Config:
        schema_extra = {
            "example": {
                "recommendations": {
                    "End Cap 1 - Beverages": 1.65,
                    "Main Entrance Display": 1.42,
                    "Checkout Lane 1": 1.38,
                    "Beverage Aisle - Eye Level": 1.25,
                    "Snack Aisle - Eye Level": 1.18
                },
                "explanation": {
                    "location": "End Cap 1 - Beverages",
                    "roi_score": 1.65,
                    "summary": "End Cap 1 provides highest ROI due to premium location visibility and high foot traffic"
                },
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "timestamp": "2025-11-17T15:45:30.123456"
            }
        }


class DefendRequest(BaseModel):
    """Request model for defend endpoint"""
    session_id: str = Field(..., description="Session ID from analyze response")
    question: str = Field(..., description="Follow-up question about recommendations")

    class Config:
        schema_extra = {
            "example": {
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "question": "Why did you recommend End Cap 1 over Checkout?"
            }
        }


class DefendResponse(BaseModel):
    """Response model for defend endpoint"""
    answer: str = Field(..., description="Detailed answer to the question")
    session_id: str = Field(..., description="Session ID")

    class Config:
        schema_extra = {
            "example": {
                "answer": "End Cap 1 was recommended over Checkout primarily due to...",
                "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
            }
        }


# API Endpoints

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Retail Product Placement Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "endpoints": {
            "analyze": "POST /api/analyze",
            "defend": "POST /api/defend",
            "competitors": "GET /api/competitors/{location_id}",
            "products": "GET /api/products",
            "locations": "GET /api/locations"
        }
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "data_loaded": {
            "products": len(data_store['products']),
            "locations": len(data_store['locations']),
            "roi_scores": len(data_store['precomputed_roi']),
            "competitors": len(data_store['competitors']),
            "historical_examples": len(data_store['historical_examples'])
        },
        "active_sessions": len(session_store)
    }


@app.post("/api/analyze", response_model=AnalyzeResponse, tags=["Analysis"])
async def analyze_placement(request: AnalyzeRequest):
    """
    Analyze product and return placement recommendations with ROI scores.

    This endpoint:
    1. Validates product input
    2. Runs the multi-agent workflow
    3. Returns top 5 location recommendations
    4. Provides detailed explanation
    5. Creates a session for follow-up questions
    """
    try:
        logger.info(f"📊 Analyzing placement for: {request.product_name}")

        # Create ProductInput
        product_input = ProductInput(
            product_name=request.product_name,
            category=request.category,
            price=request.price,
            budget=request.budget,
            target_sales=request.target_sales,
            target_customers=request.target_customers,
            expected_roi=request.expected_roi
        )

        # Execute workflow
        result = orchestrator.execute(product_input)

        if not result.recommendations:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No suitable locations found within budget constraints"
            )

        # Generate explanation (use result.explanation from orchestrator)
        explanation = result.explanation if result.explanation else _generate_simple_explanation(result)

        # Store session
        session_id = result.session_id
        session_store[session_id] = result

        # Build response
        response = AnalyzeResponse(
            recommendations=result.recommendations,
            explanation=explanation,
            session_id=session_id,
            timestamp=result.timestamp.isoformat()
        )

        logger.info(f"✅ Analysis complete. Top recommendation: {list(result.recommendations.keys())[0]}")

        return response

    except ValueError as e:
        logger.error(f"❌ Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Analysis error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.post("/api/defend", response_model=DefendResponse, tags=["Analysis"])
async def defend_recommendation(request: DefendRequest):
    """
    Answer follow-up questions about recommendations.

    This endpoint allows users to ask "why?" questions about the analysis
    and get detailed, evidence-backed explanations.
    """
    try:
        logger.info(f"❓ Defending recommendation for session: {request.session_id[:8]}...")

        # Retrieve session
        if request.session_id not in session_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found. Please run /api/analyze first."
            )

        state = session_store[request.session_id]

        # Generate answer based on question
        answer = _answer_question(state, request.question)

        response = DefendResponse(
            answer=answer,
            session_id=request.session_id
        )

        logger.info(f"✅ Question answered for session {request.session_id[:8]}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error defending recommendation: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/competitors/{location_id}", tags=["Data"])
async def get_competitors(location_id: str):
    """
    Get competitor product data for a specific location.
    """
    try:
        # Filter competitors by location
        location_competitors = [
            comp for comp in data_store['competitors']
            if comp['location_id'] == location_id
        ]

        if not location_competitors:
            return {
                "location_id": location_id,
                "competitors": [],
                "message": "No competitor data available for this location"
            }

        # Calculate stats
        avg_roi = sum(c['observed_roi'] for c in location_competitors) / len(location_competitors)

        return {
            "location_id": location_id,
            "competitors": location_competitors,
            "stats": {
                "count": len(location_competitors),
                "average_roi": round(avg_roi, 2)
            }
        }

    except Exception as e:
        logger.error(f"❌ Error fetching competitors: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/products", tags=["Data"])
async def get_products(category: Optional[str] = None, limit: int = 30):
    """
    Get product catalog, optionally filtered by category.
    """
    try:
        products = data_store['products']

        if category:
            products = [p for p in products if p['category'].lower() == category.lower()]

        return {
            "products": products[:limit],
            "count": len(products),
            "categories": list(set(p['category'] for p in data_store['products']))
        }

    except Exception as e:
        logger.error(f"❌ Error fetching products: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/locations", tags=["Data"])
async def get_locations():
    """
    Get all available shelf locations.
    """
    try:
        return {
            "locations": data_store['locations'],
            "count": len(data_store['locations'])
        }

    except Exception as e:
        logger.error(f"❌ Error fetching locations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


# Helper functions

def _generate_simple_explanation(result) -> Dict[str, Any]:
    """Generate simple explanation for top recommendation"""

    if not result.recommendations:
        return {"summary": "No recommendations available"}

    top_location = list(result.recommendations.keys())[0]
    top_roi = result.recommendations[top_location]

    # Get location details
    location_details = next(
        (loc for loc in data_store['locations'] if loc['zone_name'] == top_location),
        None
    )

    # Generate explanation
    explanation = {
        "location": top_location,
        "roi_score": top_roi,
        "summary": f"{top_location} provides highest predicted ROI of {top_roi:.2f}",
        "key_factors": [],
        "confidence_interval": None
    }

    # Add key factors if location found
    if location_details:
        explanation["key_factors"] = [
            f"Zone Type: {location_details['zone_type']} (premium visibility)",
            f"Traffic Level: {location_details['traffic_level'].capitalize()} ({location_details['traffic_index']} daily visitors)",
            f"Visibility Factor: {location_details['visibility_factor']}x multiplier"
        ]

    return explanation


def _answer_question(result, question: str) -> str:
    """Answer user questions about recommendations"""

    question_lower = question.lower()

    # Pattern matching for common questions
    if "why" in question_lower and "recommend" in question_lower:
        # Why was X recommended?
        top_location = list(result.recommendations.keys())[0]
        top_roi = result.recommendations[top_location]

        location_details = next(
            (loc for loc in data_store['locations'] if loc['zone_name'] == top_location),
            None
        )

        if location_details:
            answer = f"**{top_location}** was recommended as the top choice (ROI: {top_roi:.2f}) due to several key factors:\n\n"
            answer += f"1. **Premium Location**: This is a {location_details['zone_type']} location with {location_details['visibility_factor']}x visibility multiplier\n"
            answer += f"2. **High Traffic**: {location_details['traffic_level'].capitalize()} traffic area with {location_details['traffic_index']} daily visitor index\n"
            answer += f"3. **Category Alignment**: "

            if location_details['primary_category'] == state.product.category:
                answer += f"Perfect match - this location specializes in {location_details['primary_category']}\n"
            else:
                answer += f"Good cross-category opportunity\n"

            answer += f"4. **Budget Fit**: Placement cost fits within your ${state.product.budget:.2f} budget\n"

            return answer
        else:
            return f"**{top_location}** was recommended based on ROI analysis showing {top_roi:.2f}x return on investment."

    elif "competitor" in question_lower or "vs" in question_lower:
        # Competitor comparison
        top_location = list(state.final_recommendations.keys())[0]

        # Find competitors for this location
        location_id = next(
            (loc['location_id'] for loc in data_store['locations'] if loc['zone_name'] == top_location),
            None
        )

        if location_id:
            location_competitors = [
                comp for comp in data_store['competitors']
                if comp['location_id'] == location_id and comp['category'] == state.product.category
            ]

            if location_competitors:
                avg_comp_roi = sum(c['observed_roi'] for c in location_competitors) / len(location_competitors)
                predicted_roi = state.final_recommendations[top_location]

                answer = f"**Competitor Analysis for {top_location}:**\n\n"
                answer += f"Currently, there are **{len(location_competitors)} competitor products** in this location:\n\n"

                for comp in location_competitors[:3]:
                    answer += f"- {comp['product_name']}: ROI {comp['observed_roi']:.2f}\n"

                answer += f"\n**Average Competitor ROI**: {avg_comp_roi:.2f}\n"
                answer += f"**Your Predicted ROI**: {predicted_roi:.2f}\n\n"

                if predicted_roi > avg_comp_roi:
                    diff_pct = ((predicted_roi / avg_comp_roi) - 1) * 100
                    answer += f"✅ Your product is predicted to **outperform** competitors by **{diff_pct:.0f}%**"
                else:
                    diff_pct = ((avg_comp_roi / predicted_roi) - 1) * 100
                    answer += f"⚠️ Competitors currently outperform by **{diff_pct:.0f}%**, but this location still offers the best ROI for your budget"

                return answer
            else:
                return f"No competitor data available for {top_location} in the {state.product.category} category."

        return "Unable to retrieve competitor information."

    elif "alternative" in question_lower or "other" in question_lower or "second" in question_lower:
        # Alternative locations
        if len(state.final_recommendations) > 1:
            locations = list(state.final_recommendations.items())

            answer = "**Alternative Placement Options:**\n\n"

            for i, (loc, roi) in enumerate(locations[1:4], 2):  # Top 2-4
                answer += f"**#{i}: {loc}** (ROI: {roi:.2f})\n"

                # Get location details
                loc_details = next(
                    (l for l in data_store['locations'] if l['zone_name'] == loc),
                    None
                )

                if loc_details:
                    answer += f"   - Type: {loc_details['zone_type']}, Traffic: {loc_details['traffic_level']}\n"

                # Compare to top recommendation
                top_roi = locations[0][1]
                diff = top_roi - roi
                diff_pct = (diff / top_roi) * 100
                answer += f"   - {diff:.2f} lower ROI than top choice ({diff_pct:.0f}% difference)\n\n"

            return answer
        else:
            return "Only one location was found within your budget constraints."

    elif "confidence" in question_lower or "sure" in question_lower or "certain" in question_lower:
        # Confidence assessment
        top_location = list(state.final_recommendations.keys())[0]

        if state.roi_predictions and top_location in state.roi_predictions:
            pred = state.roi_predictions[top_location]
            roi = pred.roi
            lower, upper = pred.confidence_interval

            ci_width = upper - lower
            relative_width = ci_width / roi

            answer = f"**Confidence Assessment for {top_location}:**\n\n"
            answer += f"- **Predicted ROI**: {roi:.2f}\n"
            answer += f"- **80% Confidence Interval**: [{lower:.2f}, {upper:.2f}]\n"
            answer += f"- **Interval Width**: {ci_width:.2f} ({relative_width*100:.0f}% of prediction)\n\n"

            if relative_width < 0.15:
                answer += "✅ **High confidence**: Narrow interval indicates strong prediction certainty."
            elif relative_width < 0.30:
                answer += "⚠️ **Moderate confidence**: Reasonable uncertainty, typical for retail predictions."
            else:
                answer += "⚠️ **Lower confidence**: Wide interval suggests higher uncertainty."

            return answer

        return "Confidence interval information not available."

    else:
        # Generic answer
        return f"Based on your question, I recommend reviewing the top recommendation: **{list(state.final_recommendations.keys())[0]}** with ROI of {list(state.final_recommendations.values())[0]:.2f}. For more specific information, please ask about competitors, alternatives, or confidence levels."


if __name__ == "__main__":
    import uvicorn

    print("🚀 Starting Retail Placement API Server...")
    print("📖 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/api/health")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
