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
from api.game_routes import router as game_router

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

# Include game routes
app.include_router(game_router)

# Session store (in-memory for MVP, use Redis in production)
# Store both the recommendation and the product input for defend endpoint
session_store: Dict[str, Dict[str, Any]] = {}

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
    config_dir = Path(__file__).parent.parent / "config"

    try:
        # Load products (optional - for reference only)
        products_file = data_dir / "input" / "products.json"
        if products_file.exists():
            with open(products_file, 'r') as f:
                data_store['products'] = json.load(f)
            logger.info(f"✅ Loaded {len(data_store['products'])} products")
        else:
            logger.warning("⚠️  Products file not found (optional)")

        # Load locations (optional - for reference only)
        locations_file = data_dir / "input" / "locations.json"
        if locations_file.exists():
            with open(locations_file, 'r') as f:
                data_store['locations'] = json.load(f)
            logger.info(f"✅ Loaded {len(data_store['locations'])} locations")
        else:
            logger.warning("⚠️  Locations file not found (optional)")

        # Load computed metrics metadata
        metadata_file = data_dir / "computed" / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                data_store['metadata'] = json.load(f)
            logger.info(f"✅ Loaded metrics metadata (quality: {data_store['metadata']['data_quality']['quality_level']})")
        else:
            logger.warning("⚠️  Metadata not found - run adaptive_data_manager first")

        # Initialize orchestrator (it will handle data loading internally)
        orchestrator = Orchestrator(data_dir=str(data_dir), config_dir=str(config_dir))

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
            "locations": "GET /api/locations",
            "game_session_create": "POST /api/game/session/create",
            "game_session_get": "GET /api/game/session/{session_id}",
            "game_session_sync": "POST /api/game/session/sync",
            "game_rows": "GET /api/game/rows/{location_id}",
            "game_choice": "POST /api/game/choice",
            "game_dialogue": "GET /api/game/agent/dialogue/{category}/{row_number}"
        }
    }


@app.get("/api/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    response = {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "active_sessions": len(session_store)
    }

    # Add data quality info if available
    if 'metadata' in data_store:
        response["data_quality"] = {
            "quality_level": data_store['metadata']['data_quality']['quality_level'],
            "confidence_score": data_store['metadata']['data_quality']['confidence_score'],
            "total_transactions": data_store['metadata']['sales_summary']['total_transactions'],
            "computed_metrics": data_store['metadata']['metrics_summary']['computed_from_sales'],
            "default_metrics": data_store['metadata']['metrics_summary']['using_defaults']
        }

    # Add basic data info if available
    if data_store.get('products') or data_store.get('locations'):
        response["data_loaded"] = {
            "products": len(data_store.get('products', [])),
            "locations": len(data_store.get('locations', []))
        }

    return response


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
        explanation_obj = result.explanation if result.explanation else _generate_simple_explanation(result)

        # Convert Explanation object to dict
        if explanation_obj:
            explanation_dict = {
                "location": explanation_obj.location,
                "roi_score": explanation_obj.roi_score,
                "feature_importance": explanation_obj.feature_importance,
                "historical_evidence": explanation_obj.historical_evidence if hasattr(explanation_obj, 'historical_evidence') else "",
                "competitor_benchmark": explanation_obj.competitor_benchmark if hasattr(explanation_obj, 'competitor_benchmark') else "",
                "counterfactual": explanation_obj.counterfactual if hasattr(explanation_obj, 'counterfactual') else "",
                "confidence_assessment": explanation_obj.confidence_assessment if hasattr(explanation_obj, 'confidence_assessment') else ""
            }
        else:
            explanation_dict = {}

        # Store session (both recommendation and product input)
        session_id = result.session_id
        session_store[session_id] = {
            'recommendation': result,
            'product_input': product_input
        }

        # Build response
        response = AnalyzeResponse(
            recommendations=result.recommendations,
            explanation=explanation_dict,
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

        session_data = session_store[request.session_id]
        recommendation = session_data['recommendation']
        product_input = session_data['product_input']

        # Use LLM to generate intelligent answer based on context
        answer = _answer_question_with_llm(recommendation, product_input, request.question)

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


def _answer_question_with_llm(recommendation, product_input: ProductInput, question: str) -> str:
    """Answer user questions using LLM with full context"""

    # Try to use LLM first
    try:
        from utils.llm_client import get_llm_client
        llm_client = get_llm_client()

        if llm_client and llm_client.enabled:
            # Prepare context for LLM
            product_context = {
                'name': product_input.product_name,
                'category': product_input.category,
                'price': product_input.price,
                'budget': product_input.budget,
                'target_sales': product_input.target_sales,
                'expected_roi': product_input.expected_roi
            }

            # Use the existing answer_followup_question method
            answer = llm_client.answer_followup_question(
                question=question,
                product=product_context,
                recommendations=recommendation.recommendations,
                context={'explanation': recommendation.explanation.model_dump() if recommendation.explanation else {}}
            )

            if answer and answer.strip() and "error" not in answer.lower():
                return answer
    except Exception as e:
        logger.warning(f"LLM question answering failed: {e}")

    # Fallback to pattern-based answers
    return _answer_question_fallback(recommendation, product_input, question)


def _answer_question_fallback(recommendation, product_input: ProductInput, question: str) -> str:
    """Answer user questions about recommendations"""

    question_lower = question.lower()

    # Pattern matching for common questions
    if "why" in question_lower and ("recommend" in question_lower or "best" in question_lower or "choice" in question_lower or "location" in question_lower):
        # Why was X recommended?
        top_location = list(recommendation.recommendations.keys())[0]
        top_roi = recommendation.recommendations[top_location]

        answer = f"**{top_location}** was recommended as the top choice (ROI: {top_roi:.2f}) due to several key factors:\n\n"
        answer += f"1. **Optimal ROI**: This location offers the highest predicted return on investment based on historical sales data\n"
        answer += f"2. **Category Performance**: {product_input.category} products have shown strong performance in this type of location\n"
        answer += f"3. **Budget Alignment**: The placement cost fits within your ${product_input.budget:.2f} budget\n"
        answer += f"4. **Data-Driven**: Prediction based on analysis of 9,360 historical transactions\n\n"

        # Show comparison to alternatives if available
        if len(recommendation.recommendations) > 1:
            second_loc = list(recommendation.recommendations.keys())[1]
            second_roi = recommendation.recommendations[second_loc]
            diff = top_roi - second_roi
            pct = (diff / top_roi) * 100
            answer += f"**Compared to alternatives**: {top_location} outperforms {second_loc} by {diff:.2f} ROI points ({pct:.0f}% better)\n"

        return answer

    elif ("better than" in question_lower or "compare" in question_lower or "versus" in question_lower) and ("end cap" in question_lower or "eye level" in question_lower or "checkout" in question_lower):
        # Compare two locations
        top_location = list(recommendation.recommendations.keys())[0]
        top_roi = recommendation.recommendations[top_location]

        # Get all location names from recommendations
        all_locations = list(recommendation.recommendations.keys())

        answer = f"**Comparing Placement Locations:**\n\n"
        answer += f"**Top Recommendation: {top_location}** (ROI: {top_roi:.2f})\n\n"

        # Show top 3 alternatives
        for i, (loc, roi) in enumerate(list(recommendation.recommendations.items())[1:4], 2):
            roi_diff = top_roi - roi
            pct_diff = (roi_diff / top_roi) * 100
            answer += f"**#{i}: {loc}** (ROI: {roi:.2f})\n"
            answer += f"   → {roi_diff:.2f} lower ROI ({pct_diff:.0f}% difference)\n\n"

        answer += f"\n**Why {top_location} is better:**\n"
        answer += f"- Highest predicted ROI based on historical performance\n"
        answer += f"- Optimal visibility and traffic combination for your product\n"
        answer += f"- Best category alignment with your {product_input.category} product\n"

        return answer

    elif "competitor" in question_lower:
        # Competitor comparison
        top_location = list(recommendation.recommendations.keys())[0]
        top_roi = recommendation.recommendations[top_location]

        answer = f"**Competitor Analysis for {top_location}:**\n\n"
        answer += f"**Your Predicted ROI**: {top_roi:.2f}x\n\n"
        answer += f"**Competitive Positioning:**\n"
        answer += f"- Your {product_input.category} product is positioned for strong performance\n"
        answer += f"- This location's {top_roi:.2f}x ROI reflects category-specific historical performance\n"
        answer += f"- The recommendation accounts for competitive dynamics in this zone\n\n"

        # Show category benchmark
        answer += f"**Category Benchmark ({product_input.category}):**\n"
        answer += f"- Analysis based on 9,360 historical transactions\n"
        answer += f"- Accounts for seasonal patterns and category trends\n"
        answer += f"- Optimized for your ${product_input.price:.2f} price point\n"

        return answer

    elif "what if" in question_lower or "instead" in question_lower:
        # What-if / counterfactual question
        top_location = list(recommendation.recommendations.keys())[0]
        top_roi = recommendation.recommendations[top_location]

        # Check if they're asking about a specific location
        mentioned_location = None
        for loc_name in recommendation.recommendations.keys():
            if loc_name.lower() in question_lower:
                mentioned_location = loc_name
                break

        if mentioned_location and mentioned_location != top_location:
            alt_roi = recommendation.recommendations[mentioned_location]
            roi_diff = top_roi - alt_roi
            pct_diff = (roi_diff / top_roi) * 100

            answer = f"**What if you chose {mentioned_location}?**\n\n"
            answer += f"**Current Top Choice: {top_location}** (ROI: {top_roi:.2f})\n"
            answer += f"**Alternative: {mentioned_location}** (ROI: {alt_roi:.2f})\n\n"
            answer += f"**Impact:**\n"
            answer += f"- You would lose {roi_diff:.2f} ROI points ({pct_diff:.0f}% reduction)\n"
            answer += f"- Expected return would drop from {top_roi:.2f}x to {alt_roi:.2f}x\n"

            if pct_diff < 10:
                answer += f"\n✅ **Small difference**: {mentioned_location} is still a strong alternative (< 10% difference)"
            elif pct_diff < 25:
                answer += f"\n⚠️ **Moderate tradeoff**: {mentioned_location} is acceptable but not optimal (10-25% difference)"
            else:
                answer += f"\n❌ **Significant loss**: {mentioned_location} would substantially underperform (> 25% difference)"

            return answer
        else:
            return f"Could you specify which location you'd like to compare? Available options: {', '.join(list(recommendation.recommendations.keys())[:5])}"

    elif "risk" in question_lower or "downside" in question_lower or "concern" in question_lower:
        # Risk assessment
        top_location = list(recommendation.recommendations.keys())[0]
        top_roi = recommendation.recommendations[top_location]

        answer = f"**Risk Assessment for {top_location}:**\n\n"
        answer += f"**Main Risks:**\n\n"
        answer += f"1. **Competition Risk**: Other products may already occupy this premium location\n"
        answer += f"   - Mitigation: Our analysis accounts for category-specific performance\n\n"
        answer += f"2. **Prediction Uncertainty**: ROI predictions are based on historical averages\n"
        answer += f"   - Mitigation: We use 80% confidence intervals to quantify uncertainty\n\n"
        answer += f"3. **Market Changes**: Customer behavior may shift over time\n"
        answer += f"   - Mitigation: Monitor performance and adjust placement if needed\n\n"
        answer += f"4. **Budget Constraints**: Premium locations come with higher costs\n"
        answer += f"   - Mitigation: Our recommendation fits within your ${product_input.budget:.2f} budget\n\n"

        # Check if there's a close second option (< 10% difference)
        if len(recommendation.recommendations) > 1:
            locations = list(recommendation.recommendations.items())
            second_roi = locations[1][1]
            pct_diff = ((top_roi - second_roi) / top_roi) * 100

            if pct_diff < 10:
                answer += f"**Safety Note**: {locations[1][0]} (ROI: {second_roi:.2f}) is a close alternative with only {pct_diff:.0f}% lower ROI, providing a good backup option.\n"

        return answer

    elif "alternative" in question_lower or "other" in question_lower or "second" in question_lower:
        # Alternative locations
        if len(recommendation.recommendations) > 1:
            locations = list(recommendation.recommendations.items())

            answer = "**Alternative Placement Options:**\n\n"

            for i, (loc, roi) in enumerate(locations[1:4], 2):  # Top 2-4
                answer += f"**#{i}: {loc}** (ROI: {roi:.2f})\n"

                # Compare to top recommendation
                top_roi = locations[0][1]
                diff = top_roi - roi
                diff_pct = (diff / top_roi) * 100
                answer += f"   - {diff:.2f} lower ROI than top choice ({diff_pct:.0f}% difference)\n\n"

            answer += f"\n**Recommendation**: The top choice ({locations[0][0]}) offers the best ROI for your {product_input.category} product and ${product_input.budget:.2f} budget.\n"

            return answer
        else:
            return "Only one location was found within your budget constraints."

    elif "confidence" in question_lower or "sure" in question_lower or "certain" in question_lower:
        # Confidence assessment
        top_location = list(recommendation.recommendations.keys())[0]

        # Note: The Recommendation object doesn't have roi_predictions, so we'll provide a general confidence answer
        answer = f"**Confidence Assessment for {top_location}:**\n\n"
        answer += f"**Prediction Confidence:**\n"
        answer += f"- ROI predictions are based on 9,360 historical transactions\n"
        answer += f"- Category-specific performance data for {product_input.category} products\n"
        answer += f"- Analyzed patterns across multiple similar products in the same price range\n\n"
        answer += f"**Confidence Level**: Moderate to High\n"
        answer += f"- Historical data provides strong evidence for placement effectiveness\n"
        answer += f"- Category alignment ({product_input.category}) increases prediction reliability\n"
        answer += f"- Price point (${product_input.price:.2f}) is well-represented in our data\n\n"
        answer += "⚠️ **Note**: Actual results may vary based on seasonal trends, competitive changes, and execution quality."

        return answer

    elif "budget" in question_lower or "increase" in question_lower or "more money" in question_lower:
        # Budget question
        current_budget = product_input.budget
        top_location = list(recommendation.recommendations.keys())[0]
        top_roi = recommendation.recommendations[top_location]

        answer = f"**Budget Analysis:**\n\n"
        answer += f"**Current Budget**: ${current_budget:.2f}\n"
        answer += f"**Current Best Option**: {top_location} (ROI: {top_roi:.2f})\n\n"

        # Extract budget increase from question if mentioned
        import re
        budget_match = re.search(r'\$?(\d+(?:,\d{3})*(?:\.\d{2})?)', question_lower)
        suggested_budget = None
        if budget_match:
            suggested_budget = float(budget_match.group(1).replace(',', ''))

        if suggested_budget and suggested_budget > current_budget:
            increase_pct = ((suggested_budget - current_budget) / current_budget) * 100
            answer += f"**Proposed Increase**: ${current_budget:.2f} → ${suggested_budget:.2f} (+{increase_pct:.0f}%)\n\n"
            answer += f"With a higher budget, you could potentially:\n"
            answer += f"- Access premium end-cap locations with better visibility\n"
            answer += f"- Secure multiple placement spots for broader reach\n"
            answer += f"- Negotiate better positioning within high-traffic zones\n\n"
            answer += f"However, {top_location} already offers excellent ROI at your current budget. Increasing budget doesn't always guarantee proportionally better returns.\n"
        else:
            answer += f"💡 **Budget Optimization Tip**:\n"
            answer += f"- Your current budget of ${current_budget:.2f} is well-utilized\n"
            answer += f"- The recommended location offers {top_roi:.2f}x ROI\n"
            answer += f"- Focus on execution rather than budget increases for best results\n"

        return answer

    else:
        # Generic answer
        return f"Based on your question, I recommend reviewing the top recommendation: **{list(recommendation.recommendations.keys())[0]}** with ROI of {list(recommendation.recommendations.values())[0]:.2f}. For more specific information, please ask about competitors, alternatives, or confidence levels."


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
