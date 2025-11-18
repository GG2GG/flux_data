"""
LLM Client for OpenAI-compatible APIs
Supports OpenAI, OpenRouter, and other compatible endpoints
Includes knowledge base integration for research-backed responses
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from openai import OpenAI
from dotenv import load_dotenv
from utils.knowledge_base_loader import get_knowledge_base

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Universal LLM client for OpenAI-compatible APIs.

    Supports:
    - OpenAI (GPT-4, GPT-3.5)
    - OpenRouter (Claude, Llama, Mixtral, etc.)
    - Local LLMs (LM Studio, Ollama with OpenAI compatibility)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1500
    ):
        """
        Initialize LLM client.

        Args:
            api_key: API key (defaults to OPENAI_API_KEY or OPENROUTER_API_KEY env var)
            base_url: Base URL for API (defaults to OpenAI, can use OpenRouter)
            model: Model to use
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
        """
        # Auto-detect API key from environment
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENROUTER_API_KEY')

        if api_key is None:
            logger.warning("No API key found. LLM features will be disabled.")
            self.enabled = False
            return

        # Auto-detect base URL from environment
        if base_url is None:
            base_url = os.getenv('OPENAI_API_BASE')
            if base_url:
                logger.info(f"Using custom base URL: {base_url}")
            elif os.getenv('OPENROUTER_API_KEY'):
                base_url = "https://openrouter.ai/api/v1"
                logger.info("Using OpenRouter API")

        self.enabled = True
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize OpenAI client (compatible with OpenRouter)
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        logger.info(f"LLM Client initialized with model: {model}")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> str:
        """
        Generate text completion.

        Args:
            prompt: User prompt
            system_prompt: System prompt (optional)
            temperature: Override default temperature
            max_tokens: Override default max tokens
            json_mode: Force JSON response format

        Returns:
            Generated text
        """
        if not self.enabled:
            logger.warning("LLM client not enabled, returning empty response")
            return ""

        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            # Prepare request parameters
            kwargs = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature or self.temperature,
                "max_tokens": max_tokens or self.max_tokens
            }

            # Add JSON mode if requested (only for supported models)
            if json_mode and "gpt-4" in self.model.lower():
                kwargs["response_format"] = {"type": "json_object"}

            # Make API call
            logger.debug(f"Calling LLM with model: {kwargs['model']}, max_tokens: {kwargs.get('max_tokens')}")
            response = self.client.chat.completions.create(**kwargs)

            content = response.choices[0].message.content
            logger.debug(f"LLM raw response: {content[:200] if content else 'None'}")

            if not content or content.strip() == "":
                logger.warning("LLM returned empty content")
                return ""

            return content.strip()

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return f"Error generating response: {str(e)}"

    def generate_json(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate JSON response.

        Args:
            prompt: User prompt
            system_prompt: System prompt
            temperature: Sampling temperature

        Returns:
            Parsed JSON dict
        """
        # Add JSON instruction to system prompt
        json_system = (system_prompt or "") + "\n\nYou must respond with valid JSON only."

        response_text = self.generate(
            prompt=prompt,
            system_prompt=json_system,
            temperature=temperature,
            json_mode=True
        )

        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response: {response_text[:200]}")
            return {"error": "Invalid JSON response"}

    def analyze_product_placement(
        self,
        product: Dict[str, Any],
        location: Dict[str, Any],
        roi_score: float,
        context: Dict[str, Any]
    ) -> str:
        """
        Generate natural language analysis of product placement.

        Args:
            product: Product details
            location: Location details
            roi_score: Predicted ROI score
            context: Additional context (historical data, competitors, etc.)

        Returns:
            Natural language explanation
        """
        system_prompt = """You are an expert retail analyst specializing in product placement optimization.
Provide SHORT, CONCISE, and FACTUAL explanations (3-5 bullet points maximum).

Focus on:
- WHY this placement works (data-driven)
- Top 3 success factors only
- 1-2 key considerations

Use professional business language. Be direct and brief. NO lengthy paragraphs or sections."""

        user_prompt = f"""Product: {product['name']} (${product['price']:.2f}, {product['category']})
Location: {location['zone_name']} ({location['zone_type']})
Traffic: {location['traffic_level']} ({location['traffic_index']} visitors/day)
Visibility: {location['visibility_factor']}x
ROI: {roi_score:.2f}x

Explain in 3-5 SHORT bullet points why this placement works. Be concise and factual."""

        return self.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=1000
        )

    def generate_competitive_analysis(
        self,
        product: Dict[str, Any],
        location: Dict[str, Any],
        competitors: List[Dict[str, Any]],
        predicted_roi: float
    ) -> str:
        """
        Generate competitive analysis comparing product to competitors.

        Args:
            product: Product details
            location: Location details
            competitors: List of competitor products
            predicted_roi: Predicted ROI for the product

        Returns:
            Natural language competitive analysis
        """
        system_prompt = """You are a competitive intelligence analyst for retail product placement.
Analyze competitive positioning and provide strategic insights.

Focus on:
- Market position relative to competitors
- Pricing strategy implications
- Differentiation opportunities
- Competitive advantages/disadvantages
- Strategic recommendations"""

        competitor_summary = "\n".join([
            f"- {c['product_name']}: ${c['price']:.2f}, ROI {c['observed_roi']:.2f}"
            for c in competitors[:5]
        ])

        avg_competitor_roi = sum(c['observed_roi'] for c in competitors) / len(competitors) if competitors else 0

        user_prompt = f"""Analyze competitive positioning for this product placement:

**Our Product:**
- {product['name']} (${product['price']:.2f})
- Predicted ROI: {predicted_roi:.2f}

**Location:** {location['zone_name']}

**Competitors in this location ({len(competitors)} total):**
{competitor_summary}

**Average Competitor ROI:** {avg_competitor_roi:.2f}

Provide strategic analysis of our competitive position and recommendations for success."""

        return self.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7
        )

    def answer_followup_question(
        self,
        question: str,
        product: Dict[str, Any],
        recommendations: Dict[str, float],
        context: Dict[str, Any],
        use_knowledge_base: bool = True
    ) -> str:
        """
        Answer follow-up questions about recommendations using LLM.

        Args:
            question: User's question
            product: Product details
            recommendations: ROI recommendations
            context: Additional context (competitors, historical data, etc.)
            use_knowledge_base: Whether to include research-backed insights

        Returns:
            Natural language answer
        """
        system_prompt = """You are a retail analytics expert. Answer questions about product placement recommendations.

Be SHORT and CONCISE (3-5 sentences maximum):
- Use specific numbers from the analysis
- Be factual and data-driven
- Cite research when available (e.g., "Research shows...")
- Professional business language
- Direct answers only

NO lengthy paragraphs or unnecessary details."""

        recommendations_text = "\n".join([
            f"- {loc}: ROI {roi:.2f}"
            for loc, roi in list(recommendations.items())[:5]
        ])

        # Get research-backed insights from knowledge base
        research_context = ""
        if use_knowledge_base:
            try:
                kb = get_knowledge_base()
                research_context = kb.get_context_for_llm(question, max_sources=2, include_citations=False)
            except Exception as e:
                logger.warning(f"Failed to load knowledge base: {e}")

        user_prompt = f"""Question: {question}

Product: {product['name']} (${product['price']:.2f}, {product['category']}, Budget: ${product.get('budget', 'N/A')})

Top Recommendations:
{recommendations_text}

Analysis Context: {json.dumps(context, indent=2) if context else 'Basic analysis only'}

{research_context}

Answer in 3-5 concise sentences with specific data points. If research is provided, reference it naturally (e.g., "Studies show...")."""

        return self.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.5,
            max_tokens=500
        )

    def generate_insight_summary(
        self,
        product: Dict[str, Any],
        top_locations: List[Dict[str, Any]],
        roi_scores: Dict[str, float],
        historical_performance: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Generate executive summary of placement insights.

        Args:
            product: Product details
            top_locations: Top recommended locations
            roi_scores: ROI scores for locations
            historical_performance: Historical data (optional)

        Returns:
            Structured insight summary
        """
        system_prompt = """You are an executive analyst preparing a placement strategy summary.
Generate a JSON response with these sections:

{
  "executive_summary": "2-3 sentence overview",
  "key_insights": ["insight 1", "insight 2", "insight 3"],
  "success_factors": ["factor 1", "factor 2", "factor 3"],
  "risks": ["risk 1", "risk 2"],
  "recommendation": "Primary recommendation with rationale"
}"""

        locations_text = "\n".join([
            f"- {loc['zone_name']}: ROI {roi_scores.get(loc['zone_name'], 0):.2f}"
            for loc in top_locations[:3]
        ])

        user_prompt = f"""Generate executive summary for this placement analysis:

Product: {product['name']} (${product['price']:.2f}, {product['category']})
Budget: ${product.get('budget', 'unknown')}

Top Locations:
{locations_text}

Respond with JSON only."""

        return self.generate_json(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.5
        )


# Global LLM client instance
_llm_client: Optional[LLMClient] = None


def get_llm_client() -> LLMClient:
    """Get or create global LLM client instance."""
    global _llm_client

    if _llm_client is None:
        # Try to initialize with available API keys
        api_key = os.getenv('OPENAI_API_KEY') or os.getenv('OPENROUTER_API_KEY')
        base_url = os.getenv('OPENAI_API_BASE')
        model = os.getenv('LLM_MODEL', "gpt-4o-mini")
        temperature = float(os.getenv('LLM_TEMPERATURE', '0.7'))
        max_tokens = int(os.getenv('LLM_MAX_TOKENS', '1500'))

        # Use OpenRouter if available (and no custom base URL)
        if os.getenv('OPENROUTER_API_KEY') and not base_url:
            base_url = "https://openrouter.ai/api/v1"
            if model == "gpt-4o-mini":  # Default model, use Claude for OpenRouter
                model = "anthropic/claude-3.5-sonnet"

        _llm_client = LLMClient(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens
        )

    return _llm_client


def set_llm_client(client: LLMClient):
    """Set global LLM client instance."""
    global _llm_client
    _llm_client = client
