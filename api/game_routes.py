"""
Unity Game Integration Routes for Retail Placement API
Handles bidirectional communication between Unity WebGL game and web interface
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/game", tags=["Unity Game Integration"])

# Game session store (in-memory for MVP, use Redis in production)
game_sessions: Dict[str, Dict] = {}

# Session expiration time (24 hours)
SESSION_EXPIRATION = timedelta(hours=24)


# ==================== REQUEST/RESPONSE MODELS ====================

class GameSessionCreateRequest(BaseModel):
    """Request to create a new game session"""
    product_name: str = Field(..., description="Product name")
    category: str = Field(..., description="Product category")
    price: float = Field(..., gt=0, description="Product price")
    budget: float = Field(..., gt=0, description="Placement budget")
    target_sales: int = Field(..., gt=0, description="Target sales units")
    expected_roi: float = Field(..., gt=0, description="Expected ROI")

    class Config:
        schema_extra = {
            "example": {
                "product_name": "Premium Energy Drink",
                "category": "Beverages",
                "price": 3.49,
                "budget": 5000.00,
                "target_sales": 1000,
                "expected_roi": 1.5
            }
        }


class UnityDataConfig(BaseModel):
    """Unity-specific configuration data"""
    product_sprite_url: str
    product_color: str
    starting_budget: float
    target_revenue: float


class GameSessionResponse(BaseModel):
    """Response after creating game session"""
    session_id: str
    unity_data: UnityDataConfig
    web_url: str
    created_at: str


class SessionSyncRequest(BaseModel):
    """Request to sync session state"""
    session_id: str
    sync_data: Dict[str, Any] = Field(..., description="Data to sync (player_choice, dialogue_state, etc.)")


class SessionSyncResponse(BaseModel):
    """Response after syncing session"""
    synced: bool
    web_state_updated: bool
    timestamp: str


class ChoiceRequest(BaseModel):
    """Request to record player's placement choice"""
    session_id: str
    location_id: str
    row_number: int
    choice_timestamp: str
    dialogue_path: Optional[str] = None


class ChoiceResponse(BaseModel):
    """Response after recording choice"""
    choice_recorded: bool
    roi_result: float
    success_message: str
    web_redirect: str
    next_recommendation: Optional[Dict[str, Any]] = None


class DialogueLine(BaseModel):
    """Single line of dialogue"""
    speaker: str
    text: str
    emotion: str
    duration_seconds: int
    data_source: Optional[str] = None


class VisualCues(BaseModel):
    """Visual feedback cues for Unity"""
    highlight_shelf: bool
    show_roi_badge: bool
    particle_effect: Optional[str] = None


class DialogueResponse(BaseModel):
    """Agent dialogue response"""
    category: str
    row_number: int
    dialogue_lines: List[DialogueLine]
    visual_cues: VisualCues


# ==================== HELPER FUNCTIONS ====================

def get_category_color(category: str) -> str:
    """Map category to color for Unity visualization"""
    colors = {
        "beverages": "#3B82F6",  # Blue
        "snacks": "#F59E0B",      # Orange
        "dairy": "#10B981",       # Green
        "bakery": "#F59E0B",      # Warm orange
        "personal care": "#8B5CF6", # Purple
        "general merchandise": "#6B7280", # Gray
        "health & beauty": "#EC4899" # Pink
    }
    return colors.get(category.lower(), "#4F46E5")


def get_category_sprite_url(category: str) -> str:
    """Get sprite URL for product category"""
    sprites = {
        "beverages": "/assets/sprites/beverage_icon.png",
        "snacks": "/assets/sprites/snack_icon.png",
        "dairy": "/assets/sprites/dairy_icon.png",
        "bakery": "/assets/sprites/bakery_icon.png",
        "personal care": "/assets/sprites/personal_care_icon.png"
    }
    return sprites.get(category.lower(), "/assets/sprites/default_product.png")


def map_category_to_location_id(category: str) -> str:
    """Map product category to default location ID"""
    mapping = {
        "beverages": "loc_001",
        "snacks": "loc_003",
        "dairy": "loc_006",
        "bakery": "loc_007",
        "personal care": "loc_009",
        "health & beauty": "loc_009",
        "general merchandise": "loc_010"
    }
    return mapping.get(category.lower(), "loc_005")


def cleanup_expired_sessions():
    """Remove expired sessions from memory"""
    current_time = datetime.now()
    expired_sessions = []

    for session_id, session_data in game_sessions.items():
        created_at = datetime.fromisoformat(session_data['created_at'])
        if current_time - created_at > SESSION_EXPIRATION:
            expired_sessions.append(session_id)

    for session_id in expired_sessions:
        del game_sessions[session_id]
        logger.info(f"🗑️ Removed expired session: {session_id}")


# ==================== API ENDPOINTS ====================

@router.post("/session/create", response_model=GameSessionResponse)
async def create_game_session(request: GameSessionCreateRequest):
    """
    Create a new game session for Unity integration.

    This endpoint:
    1. Generates unique session ID
    2. Creates Unity-specific configuration
    3. Stores session data for cross-system sync
    4. Returns web URL for later access
    """
    try:
        # Clean up expired sessions periodically
        cleanup_expired_sessions()

        # Generate session ID
        session_id = f"game_{uuid.uuid4().hex[:12]}"

        # Create Unity data config
        unity_data = UnityDataConfig(
            product_sprite_url=get_category_sprite_url(request.category),
            product_color=get_category_color(request.category),
            starting_budget=request.budget,
            target_revenue=request.budget * request.expected_roi
        )

        # Store game session
        game_sessions[session_id] = {
            "session_id": session_id,
            "product_data": request.dict(),
            "unity_data": unity_data.dict(),
            "created_at": datetime.now().isoformat(),
            "game_progress": {
                "choices_made": 0,
                "current_location": None,
                "total_playtime_seconds": 0,
                "dialogue_state": "inactive"
            },
            "web_interactions": {
                "locations_viewed": [],
                "shelves_expanded": 0
            },
            "status": "active"
        }

        # Generate web URL
        web_url = f"http://localhost:8080/demo/planogram_final.html?session={session_id}"

        response = GameSessionResponse(
            session_id=session_id,
            unity_data=unity_data,
            web_url=web_url,
            created_at=game_sessions[session_id]['created_at']
        )

        logger.info(f"🎮 Game session created: {session_id} for {request.product_name}")

        return response

    except Exception as e:
        logger.error(f"❌ Error creating game session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create game session: {str(e)}"
        )


@router.get("/session/{session_id}")
async def get_game_session(session_id: str):
    """
    Retrieve game session data.

    Used by web interface to load existing game session.
    """
    try:
        if session_id not in game_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Game session {session_id} not found"
            )

        session_data = game_sessions[session_id]

        # Check if session expired
        created_at = datetime.fromisoformat(session_data['created_at'])
        if datetime.now() - created_at > SESSION_EXPIRATION:
            del game_sessions[session_id]
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Game session expired (24 hour limit)"
            )

        return session_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error retrieving game session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session: {str(e)}"
        )


@router.post("/session/sync", response_model=SessionSyncResponse)
async def sync_game_session(request: SessionSyncRequest):
    """
    Synchronize session state between Unity and web.

    Updates game progress, dialogue state, and web interactions.
    """
    try:
        session_id = request.session_id

        if session_id not in game_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        session = game_sessions[session_id]

        # Update sync data
        sync_data = request.sync_data

        # Update game progress if provided
        if "dialogue_state" in sync_data:
            session['game_progress']['dialogue_state'] = sync_data['dialogue_state']

        if "current_location" in sync_data:
            session['game_progress']['current_location'] = sync_data['current_location']

        if "playtime_seconds" in sync_data:
            session['game_progress']['total_playtime_seconds'] = sync_data['playtime_seconds']

        # Update web interactions if provided
        if "location_viewed" in sync_data:
            if sync_data['location_viewed'] not in session['web_interactions']['locations_viewed']:
                session['web_interactions']['locations_viewed'].append(sync_data['location_viewed'])

        if "shelf_expanded" in sync_data:
            session['web_interactions']['shelves_expanded'] += 1

        # Update timestamp
        session['last_synced'] = datetime.now().isoformat()

        response = SessionSyncResponse(
            synced=True,
            web_state_updated=True,
            timestamp=session['last_synced']
        )

        logger.info(f"🔄 Session synced: {session_id}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error syncing session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to sync session: {str(e)}"
        )


@router.get("/rows/{location_id}")
async def get_rows_for_unity(
    location_id: str,
    session_id: Optional[str] = None
):
    """
    Get row analysis data formatted for Unity display.

    Returns simplified, Unity-friendly version of row data with:
    - Short descriptions for dialogue
    - ROI scores
    - Psychology insights
    - Best product types
    """
    try:
        # Load aisle rows structure
        data_dir = Path(__file__).parent.parent / "data"
        knowledge_base_dir = Path(__file__).parent.parent / "knowledge_base"

        with open(data_dir / "aisle_rows_structure.json", 'r') as f:
            aisle_data = json.load(f)

        with open(knowledge_base_dir / "retail_psychology_sources.json", 'r') as f:
            research_data = json.load(f)

        # Get product price from session if available
        product_price = 2.99
        product_category = "Beverages"

        if session_id and session_id in game_sessions:
            session = game_sessions[session_id]
            product_price = session['product_data']['price']
            product_category = session['product_data']['category']

        # Load location details from file
        location = None
        try:
            with open(data_dir / "locations.json", 'r') as f:
                locations = json.load(f)
                location = next(
                    (loc for loc in locations if loc['location_id'] == location_id),
                    None
                )
        except:
            pass

        if not location:
            # Fallback: create mock location
            location = {
                "location_id": location_id,
                "zone_name": "Store Location",
                "zone_type": "Aisle",
                "traffic_level": "medium",
                "traffic_index": 150,
                "visibility_factor": 1.0
            }

        # Calculate ROI for each row
        rows_with_unity_display = []

        for row in aisle_data['row_structure']:
            base_roi = row['base_roi_multiplier']

            # Apply modifiers
            location_modifier = 1.0
            traffic_modifier = 1.0

            if location['zone_type'].lower().replace(' ', '_') in aisle_data['location_type_modifiers']:
                location_modifier = aisle_data['location_type_modifiers'][
                    location['zone_type'].lower().replace(' ', '_')
                ]['traffic_multiplier']

            if location['traffic_level'] in aisle_data['traffic_level_modifiers']:
                traffic_modifier = aisle_data['traffic_level_modifiers'][
                    location['traffic_level']
                ]['traffic_multiplier']

            final_roi = base_roi * location_modifier * traffic_modifier

            # Create Unity-friendly short description
            roi_percent = int((final_roi - 1) * 100)

            if final_roi >= 1.2:
                quality_desc = "Premium placement zone"
            elif final_roi >= 1.0:
                quality_desc = "Good visibility position"
            else:
                quality_desc = "Standard placement area"

            short_description = f"{quality_desc} - {roi_percent:+d}% return"

            # Create dialogue text for Gambit Agent
            dialogue_text = f"{row['description']} "

            if row['row_id'] == 1:  # Eye level
                dialogue_text += f"For your {product_category}, this position will capture 70% of purchase decisions. Scientifically proven to increase visibility by 900%."
            elif row['row_id'] == 2:  # Reach level
                dialogue_text += "Works well for familiar brands but challenging for new products. Requires customers to reach up."
            elif row['row_id'] == 3:  # Touch level
                dialogue_text += "Comfortable placement encouraging product interaction. Good for tactile product categories."
            elif row['row_id'] == 4:  # Stoop level
                dialogue_text += "Budget-friendly option with 20% reduced visibility. Works for value-priced items."
            else:
                dialogue_text += f"Expect {final_roi:.2f}x return on placement investment here."

            rows_with_unity_display.append({
                "row_id": row['row_id'],
                "row_name": row['row_name'],
                "calculated_roi": round(final_roi, 2),
                "roi_percentage": roi_percent,
                "psychology_insight": row.get('psychology_insight', row['description']),
                "sales_impact": f"Affects sales by {roi_percent:+d}% compared to baseline",
                "customer_behavior": f"Visibility: {row['visibility_factor']}x, Accessibility: {row['accessibility_factor']}x",
                "best_for": ", ".join(row['typical_products'][:3]),
                "research_backed": row['source_citation'],
                "unity_display": {
                    "short_description": short_description,
                    "dialogue_text": dialogue_text
                }
            })

        return {
            "location_id": location_id,
            "location_name": location['zone_name'],
            "rows": rows_with_unity_display,
            "product_category": product_category,
            "product_price": product_price
        }

    except Exception as e:
        logger.error(f"❌ Error fetching rows for Unity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch row data: {str(e)}"
        )


@router.post("/choice", response_model=ChoiceResponse)
async def record_player_choice(request: ChoiceRequest):
    """
    Record player's shelf placement choice from Unity game.

    Logs the choice, calculates actual ROI, provides feedback,
    and generates web redirect URL.
    """
    try:
        session_id = request.session_id

        if session_id not in game_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        session = game_sessions[session_id]

        # Load row data to get actual ROI
        data_dir = Path(__file__).parent.parent / "data"
        with open(data_dir / "aisle_rows_structure.json", 'r') as f:
            aisle_data = json.load(f)

        # Find the chosen row
        chosen_row = next(
            (row for row in aisle_data['row_structure'] if row['row_id'] == request.row_number),
            None
        )

        if not chosen_row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid row number: {request.row_number}"
            )

        # Calculate ROI (simplified for MVP)
        base_roi = chosen_row['base_roi_multiplier']
        roi_result = base_roi * 1.1  # Apply location modifier

        # Generate success message
        roi_percent = int((roi_result - 1) * 100)

        if roi_result >= 1.2:
            success_message = f"Excellent choice! {chosen_row['row_name']} will give you {roi_result:.2f}x ROI ({roi_percent:+d}% return)."
        elif roi_result >= 1.0:
            success_message = f"Good choice! {chosen_row['row_name']} will give you {roi_result:.2f}x ROI ({roi_percent:+d}% return)."
        else:
            success_message = f"This placement at {chosen_row['row_name']} will give you {roi_result:.2f}x ROI ({roi_percent:+d}% return). Consider eye-level for better results."

        # Update session
        session['game_progress']['choices_made'] += 1
        session['game_progress']['last_choice'] = {
            "location_id": request.location_id,
            "row_number": request.row_number,
            "roi_result": roi_result,
            "timestamp": request.choice_timestamp
        }

        # Generate web redirect URL
        web_redirect = f"http://localhost:8080/demo/planogram_final.html?session={session_id}&highlight={request.location_id}&shelf={request.row_number}"

        # Find next best recommendation (for future enhancement)
        next_recommendation = None
        if roi_result < 1.3:
            next_recommendation = {
                "location_id": "loc_008",  # Example: Beverages End Cap
                "location_name": "Beverages End Cap",
                "reason": "Consider end cap for even higher visibility (1.85x ROI potential)"
            }

        response = ChoiceResponse(
            choice_recorded=True,
            roi_result=round(roi_result, 2),
            success_message=success_message,
            web_redirect=web_redirect,
            next_recommendation=next_recommendation
        )

        logger.info(f"✅ Player choice recorded: {session_id} chose {chosen_row['row_name']} (ROI: {roi_result:.2f}x)")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error recording choice: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to record choice: {str(e)}"
        )


@router.get("/agent/dialogue/{category}/{row_number}", response_model=DialogueResponse)
async def get_agent_dialogue(category: str, row_number: int):
    """
    Get Gambit Agent dialogue for specific category and row.

    Returns contextualized dialogue lines with timing, emotion,
    and visual cues for Unity to display.
    """
    try:
        # Load row data
        data_dir = Path(__file__).parent.parent / "data"
        knowledge_base_dir = Path(__file__).parent.parent / "knowledge_base"

        with open(data_dir / "aisle_rows_structure.json", 'r') as f:
            aisle_data = json.load(f)

        with open(knowledge_base_dir / "retail_psychology_sources.json", 'r') as f:
            research_data = json.load(f)

        # Find the row
        row = next(
            (r for r in aisle_data['row_structure'] if r['row_id'] == row_number),
            None
        )

        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Row {row_number} not found"
            )

        # Generate dialogue lines based on category and row
        dialogue_lines = []

        # Opening line
        opening = DialogueLine(
            speaker="gambit_agent",
            text=f"Let me show you something interesting about {row['row_name']}...",
            emotion="confident",
            duration_seconds=3
        )
        dialogue_lines.append(opening)

        # Main insight line (category-specific)
        if category.lower() == "beverages":
            if row_number == 1:  # Eye level
                main_text = "For beverages, eye-level placement increases impulse purchases by 23%. Your product will be seen 9 times more often here than on bottom shelves."
            else:
                main_text = f"This position gives you {row['base_roi_multiplier']:.2f}x ROI. For beverages, consider moving to eye-level for maximum impact."
        elif category.lower() in ["snacks", "chips"]:
            if row_number == 1:
                main_text = "Snacks perform exceptionally well at eye level. Customers make 70% of snack decisions right here, driven by visual appeal."
            else:
                main_text = f"This shelf offers {row['base_roi_multiplier']:.2f}x return. Impulse snacks benefit most from premium visibility."
        elif category.lower() in ["dairy", "yogurt"]:
            if row_number == 3:  # Touch level
                main_text = "Dairy products at touch level encourage customers to pick up and inspect. This tactile engagement boosts sales by 18%."
            else:
                main_text = f"For dairy, this position gives {row['base_roi_multiplier']:.2f}x ROI. Consider refrigerated end caps for premium placement."
        else:
            main_text = f"{row['description']} Expected ROI: {row['base_roi_multiplier']:.2f}x based on {row['source_citation']}."

        main_insight = DialogueLine(
            speaker="gambit_agent",
            text=main_text,
            emotion="informative",
            duration_seconds=6,
            data_source=row['source_citation']
        )
        dialogue_lines.append(main_insight)

        # Closing recommendation
        if row['base_roi_multiplier'] >= 1.2:
            closing_text = "This is a premium position. I highly recommend placing your product here."
            emotion = "encouraging"
        elif row['base_roi_multiplier'] >= 1.0:
            closing_text = "This is a solid choice that will meet your ROI targets."
            emotion = "confident"
        else:
            closing_text = "This position works, but you might want to explore higher-visibility options."
            emotion = "thoughtful"

        closing = DialogueLine(
            speaker="gambit_agent",
            text=closing_text,
            emotion=emotion,
            duration_seconds=3
        )
        dialogue_lines.append(closing)

        # Visual cues
        visual_cues = VisualCues(
            highlight_shelf=True,
            show_roi_badge=True,
            particle_effect="gold_sparkle" if row['base_roi_multiplier'] >= 1.2 else None
        )

        response = DialogueResponse(
            category=category,
            row_number=row_number,
            dialogue_lines=dialogue_lines,
            visual_cues=visual_cues
        )

        logger.info(f"🗣️ Generated dialogue for {category}, Row {row_number}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating dialogue: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate dialogue: {str(e)}"
        )


@router.get("/sessions/active")
async def get_active_sessions():
    """
    Get all active game sessions (admin/debug endpoint).
    """
    try:
        cleanup_expired_sessions()

        active_sessions = []
        for session_id, session_data in game_sessions.items():
            active_sessions.append({
                "session_id": session_id,
                "product_name": session_data['product_data']['product_name'],
                "created_at": session_data['created_at'],
                "choices_made": session_data['game_progress']['choices_made'],
                "status": session_data['status']
            })

        return {
            "active_sessions": active_sessions,
            "total_count": len(active_sessions)
        }

    except Exception as e:
        logger.error(f"❌ Error fetching active sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch active sessions: {str(e)}"
        )


@router.delete("/session/{session_id}")
async def delete_game_session(session_id: str):
    """
    Delete a game session (admin/cleanup endpoint).
    """
    try:
        if session_id not in game_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )

        del game_sessions[session_id]

        logger.info(f"🗑️ Deleted game session: {session_id}")

        return {
            "deleted": True,
            "session_id": session_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete session: {str(e)}"
        )
