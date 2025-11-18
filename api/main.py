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

        # Convert Explanation Pydantic model to dict if needed
        if hasattr(explanation, 'model_dump'):
            explanation_dict = explanation.model_dump()
        elif hasattr(explanation, 'dict'):
            explanation_dict = explanation.dict()
        else:
            explanation_dict = explanation  # Already a dict

        # Store session with all necessary data for chat
        session_id = result.session_id
        session_store[session_id] = {
            'product_input': product_input,
            'recommendations': result.recommendations,
            'explanation': result.explanation,
            'timestamp': result.timestamp
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

        # Generate answer based on question
        answer = _answer_question(session_data, request.question, request.session_id)

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


@app.get("/data/aisle_rows_structure.json", tags=["Data"])
async def get_aisle_rows_structure():
    """
    Get aisle rows structure with research-backed ROI multipliers.
    """
    try:
        data_dir = Path(__file__).parent.parent / "data"
        with open(data_dir / "aisle_rows_structure.json", 'r') as f:
            aisle_data = json.load(f)
        return aisle_data

    except Exception as e:
        logger.error(f"❌ Error fetching aisle rows structure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/api/aisle/{location_id}/rows", tags=["Data"])
async def get_location_rows_with_roi(
    location_id: str,
    product_price: float = 2.99,
    session_id: Optional[str] = None
):
    """
    Get row-level ROI calculations for a specific location.

    This endpoint calculates ROI for each of the 6 shelf rows at a given location,
    taking into account:
    - Base ROI multiplier from research (eye-level = 1.23x, etc.)
    - Location type modifiers (endcap = 1.25x traffic, etc.)
    - Traffic level modifiers (high/medium/low)
    - Product price

    Args:
        location_id: The location ID (e.g., "loc_001")
        product_price: Product price for ROI calculation (default: $2.99)
        session_id: Optional session ID to use product from analysis

    Returns:
        Dict with rows and calculated ROI for each
    """
    try:
        # Load aisle rows structure
        data_dir = Path(__file__).parent.parent / "data"
        with open(data_dir / "aisle_rows_structure.json", 'r') as f:
            aisle_data = json.load(f)

        # Find the location
        location = next(
            (loc for loc in data_store['locations'] if loc['location_id'] == location_id),
            None
        )

        if not location:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Location {location_id} not found"
            )

        # Get product price from session if provided
        if session_id and session_id in session_store:
            session_data = session_store[session_id]
            product_price = session_data['product_input'].price

        # Calculate ROI for each row
        rows_with_roi = []
        for row in aisle_data['row_structure']:
            # Base ROI multiplier from research
            base_roi = row['base_roi_multiplier']

            # Location type modifier
            location_modifier = 1.0
            zone_type_key = location['zone_type'].lower().replace(' ', '_')
            if zone_type_key in aisle_data['location_type_modifiers']:
                location_modifier = aisle_data['location_type_modifiers'][zone_type_key]['traffic_multiplier']

            # Traffic level modifier
            traffic_modifier = 1.0
            if location['traffic_level'] in aisle_data['traffic_level_modifiers']:
                traffic_modifier = aisle_data['traffic_level_modifiers'][location['traffic_level']]['traffic_multiplier']

            # Calculate final ROI
            final_roi = base_roi * location_modifier * traffic_modifier
            roi_percentage = ((final_roi - 1) * 100)

            # Determine quality tier
            quality = "standard"
            if final_roi >= 1.15:
                quality = "optimal"
            elif final_roi < 0.85:
                quality = "poor"

            rows_with_roi.append({
                "row_id": row['row_id'],
                "row_name": row['row_name'],
                "height_range": row['height_range_meters'],
                "height_description": row['height_range_description'],
                "description": row['description'],
                "base_roi_multiplier": row['base_roi_multiplier'],
                "visibility_factor": row['visibility_factor'],
                "accessibility_factor": row['accessibility_factor'],
                "calculated_roi": round(final_roi, 2),
                "roi_percentage": round(roi_percentage, 1),
                "quality": quality,
                "source_citation": row['source_citation'],
                "typical_products": row['typical_products'],
                "modifiers": {
                    "location_multiplier": location_modifier,
                    "traffic_multiplier": traffic_modifier
                }
            })

        return {
            "location": {
                "location_id": location['location_id'],
                "zone_name": location['zone_name'],
                "zone_type": location['zone_type'],
                "primary_category": location['primary_category'],
                "traffic_level": location['traffic_level'],
                "traffic_index": location['traffic_index'],
                "visibility_factor": location['visibility_factor']
            },
            "rows": rows_with_roi,
            "product_price": product_price,
            "row_count": len(rows_with_roi)
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error calculating row-level ROI: {e}")
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


def _answer_question(session_data: dict, question: str, session_id: str) -> str:
    """Answer user questions using REAL Gemini AI analysis with knowledge base"""

    # Extract data from session
    recommendations = session_data['recommendations']
    product_input = session_data['product_input']
    explanation = session_data.get('explanation', {})

    # Load knowledge base for context
    data_dir = Path(__file__).parent.parent / "data"
    knowledge_base_path = Path(__file__).parent.parent / "knowledge_base"

    try:
        with open(data_dir / "aisle_rows_structure.json", 'r') as f:
            aisle_data = json.load(f)
        with open(knowledge_base_path / "retail_psychology_sources.json", 'r') as f:
            research_data = json.load(f)
    except Exception as e:
        logger.error(f"Error loading knowledge base: {e}")
        aisle_data = {}
        research_data = {}

    # Use orchestrator to get AI-driven answer
    try:
        # Create context with knowledge base
        top_location = list(recommendations.keys())[0] if recommendations else "Unknown"
        top_roi = recommendations[top_location] if top_location != "Unknown" else 0

        # Build concise prompt for ONE SENTENCE answer
        category_tip = ""
        if product_input.category in ["Beverages", "Snacks"]:
            category_tip = "impulse-driven product needing high visibility"
        elif product_input.category in ["Dairy", "Bakery"]:
            category_tip = "convenience purchase, freshness matters"
        else:
            category_tip = "planned purchase, mid-shelf acceptable"

        # Extract actual question and history separately
        actual_question = question.split("Previous conversation:")[0].strip()
        if "Regarding" in actual_question:
            actual_question = actual_question.split(": ", 1)[1] if ": " in actual_question else actual_question

        # Extract history section if present
        history_section = ""
        if "Previous conversation:" in question:
            history_section = question.split("Previous conversation:")[1].strip()
            # Remove the "Provide a varied response..." instruction from history
            if "Provide a varied response" in history_section:
                history_section = history_section.split("Provide a varied response")[0].strip()

        # Build prompt with clear separation of history and current question
        history_prompt = f"""
PREVIOUS CONVERSATION:
{history_section}

IMPORTANT: Provide a DIFFERENT perspective than previous answers. Focus on new insights, use different language, and highlight different aspects.
""" if history_section else ""

        prompt = f"""You are a retail placement expert. Answer in EXACTLY ONE clear, actionable sentence.

CONTEXT:
- Product: {product_input.product_name} ({product_input.category})
- Price: ${product_input.price}, Budget: ${product_input.budget}
- Top Placement: {top_location} with {top_roi:.2f}x ROI
- Category Type: {category_tip}
- Key Fact: Eye-level (1.2-1.4m) gives +23% sales; below eye-level drops -25%
{history_prompt}
CURRENT QUESTION: {actual_question}

ANSWER IN ONE SENTENCE with fresh insight (Start with an action verb like "Place", "Choose", "Avoid", "Position", "Consider", "Leverage", "Optimize"):"""

        # Create a minimal state object for answer_followup
        from models.schemas import PlacementState
        state = PlacementState(
            product_input=product_input,
            session_id=session_id
        )
        state.final_recommendations = recommendations
        state.explanation = explanation

        # Call Gemini AI for concise answer
        ai_answer = orchestrator.answer_followup(
            session_id=session_id,
            question=prompt,
            state=state
        )

        # Ensure it's truly one sentence (take first sentence only)
        sentences = ai_answer.split('.')
        if len(sentences) > 1:
            ai_answer = sentences[0] + '.'

        return ai_answer

    except Exception as e:
        logger.error(f"Error getting AI answer: {e}")

        # Fallback: Return explanation if available
        if isinstance(explanation, dict) and 'feature_importance' in explanation:
            return explanation['feature_importance']
        elif hasattr(explanation, 'feature_importance'):
            return explanation.feature_importance
        else:
            return f"Based on analysis, {top_location} offers the best ROI of {top_roi:.2f}x for your {product_input.category} product."



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
