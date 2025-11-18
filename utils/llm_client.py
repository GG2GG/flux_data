"""
LLM Client for OpenAI-compatible APIs
Supports OpenAI, OpenRouter, Gemini, and other compatible endpoints
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from openai import OpenAI

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ SUCCESS: Loaded environment settings from {env_path}")
    else:
        print(f"ℹ️  INFO: No .env file found at {env_path}")
        print(f"ℹ️  INFO: Using system environment variables instead")
except ImportError:
    print("ℹ️  INFO: python-dotenv not installed")
    print("ℹ️  INFO: Install with: pip install python-dotenv")

logger = logging.getLogger(__name__)

# Try to import Gemini SDK (optional)
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
    print("✅ SUCCESS: Google Gemini SDK is available and ready")
except ImportError:
    GEMINI_AVAILABLE = False
    print("❌ ERROR: Google Gemini SDK not installed")
    print("ℹ️  INFO: Install with: pip install google-generativeai")


class LLMClient:
    """
    Universal LLM client for OpenAI-compatible APIs and Gemini.

    Supports:
    - OpenAI (GPT-4, GPT-3.5)
    - OpenRouter (Claude, Llama, Mixtral, etc.)
    - Google Gemini (gemini-pro, gemini-1.5-pro)
    - Local LLMs (LM Studio, Ollama with OpenAI compatibility)
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 1500,
        provider: Optional[str] = None  # 'openai', 'gemini', 'openrouter'
    ):
        """
        Initialize LLM client.

        Args:
            api_key: API key (auto-detects from env: OPENAI_API_KEY, GEMINI_API_KEY, OPENROUTER_API_KEY)
            base_url: Base URL for API (defaults to OpenAI, can use OpenRouter)
            model: Model to use (e.g., 'gpt-4o', 'gemini-1.5-pro', 'claude-3.5-sonnet')
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens in response
            provider: Force specific provider ('openai', 'gemini', 'openrouter')
        """
        print("\n" + "="*60)
        print("🔧 INITIALIZING AI LANGUAGE MODEL")
        print("="*60)

        # Auto-detect API key and provider from environment
        if api_key is None:
            print("🔍 Looking for API keys in environment...")

            gemini_key = os.getenv('GEMINI_API_KEY')
            openai_key = os.getenv('OPENAI_API_KEY')
            openrouter_key = os.getenv('OPENROUTER_API_KEY')

            if gemini_key:
                print("✅ Found GEMINI_API_KEY")
                print(f"   Key preview: {gemini_key[:10]}...{gemini_key[-4:]}")
                api_key = gemini_key
                provider = 'gemini'
            elif openai_key:
                print("✅ Found OPENAI_API_KEY")
                print(f"   Key preview: {openai_key[:10]}...{openai_key[-4:]}")
                api_key = openai_key
                provider = 'openai'
            elif openrouter_key:
                print("✅ Found OPENROUTER_API_KEY")
                print(f"   Key preview: {openrouter_key[:10]}...{openrouter_key[-4:]}")
                api_key = openrouter_key
                provider = 'openrouter'
            else:
                api_key = None

        if api_key is None:
            print("❌ ERROR: No API key found!")
            print("ℹ️  EXPLANATION: I need an API key to talk to AI services")
            print("ℹ️  ACTION NEEDED: Please set one of these in your .env file:")
            print("   - GEMINI_API_KEY (Recommended - free tier available)")
            print("   - OPENAI_API_KEY")
            print("   - OPENROUTER_API_KEY")
            print("ℹ️  IMPACT: AI-powered explanations will be disabled")
            print("ℹ️  FALLBACK: System will use template-based explanations instead")
            print("="*60 + "\n")
            logger.warning("No API key found. LLM features will be disabled.")
            self.enabled = False
            return

        # Set provider
        self.provider = provider or 'openai'
        print(f"✅ Using AI Provider: {self.provider.upper()}")

        # Auto-detect base URL for OpenRouter
        if base_url is None and self.provider == 'openrouter':
            base_url = "https://openrouter.ai/api/v1"
            print(f"🌐 API Endpoint: {base_url}")
            logger.info("Using OpenRouter API")

        # Initialize Gemini if requested
        if self.provider == 'gemini':
            print("🤖 Setting up Google Gemini...")

            if not GEMINI_AVAILABLE:
                print("❌ ERROR: Gemini SDK not installed!")
                print("ℹ️  EXPLANATION: The Google Gemini library is missing")
                print("ℹ️  ACTION NEEDED: Run this command:")
                print("   pip install google-generativeai")
                print("="*60 + "\n")
                logger.error("Gemini requested but google-generativeai not installed")
                self.enabled = False
                return

            try:
                print("🔐 Configuring Gemini with your API key...")
                genai.configure(api_key=api_key)

                # Default to gemini-2.0-flash if model not specified or is an OpenAI model
                # Updated: gemini-pro is deprecated, using gemini-2.0-flash for speed and reliability
                if model.startswith('gpt') or model == 'gpt-4o-mini':
                    original_model = model
                    model = 'gemini-2.0-flash'
                    print(f"ℹ️  Auto-switched model: {original_model} → {model}")

                print(f"🎯 Selected Model: {model}")
                self.gemini_model = genai.GenerativeModel(model)
                print("✅ Gemini initialized successfully!")
                print("ℹ️  WHAT THIS MEANS: AI will provide natural language explanations")
                logger.info(f"Using Gemini API with model: {model}")

            except Exception as e:
                print(f"❌ ERROR initializing Gemini: {str(e)}")
                print("ℹ️  POSSIBLE CAUSES:")
                print("   1. Invalid API key")
                print("   2. Network connection issue")
                print("   3. Gemini API is down")
                print("ℹ️  ACTION: Check your API key and internet connection")
                print("="*60 + "\n")
                self.enabled = False
                return

        self.enabled = True
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Initialize OpenAI client (compatible with OpenRouter) - only if not Gemini
        if self.provider != 'gemini':
            print("🔧 Initializing OpenAI-compatible client...")
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
            print(f"✅ Client ready with model: {model}")

        print(f"📊 Configuration:")
        print(f"   • Temperature: {temperature} (creativity level)")
        print(f"   • Max Tokens: {max_tokens} (response length)")
        print("✅ AI SYSTEM READY TO USE!")
        print("="*60 + "\n")
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
            # Use Gemini API if provider is gemini
            if self.provider == 'gemini':
                return self._generate_gemini(prompt, system_prompt, temperature, max_tokens, json_mode)

            # OpenAI/OpenRouter path
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
            response = self.client.chat.completions.create(**kwargs)

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return f"Error generating response: {str(e)}"

    def _generate_gemini(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        json_mode: bool = False
    ) -> str:
        """Generate text using Gemini API."""
        try:
            print("🤖 Asking Gemini AI for response...")
            print(f"📝 Prompt length: {len(prompt)} characters")

            # Combine system and user prompts for Gemini
            full_prompt = ""
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
                print(f"📋 System prompt included ({len(system_prompt)} chars)")
            else:
                full_prompt = prompt

            if json_mode:
                full_prompt += "\n\nPlease respond in valid JSON format."
                print("🔧 JSON mode enabled")

            # Configure generation
            generation_config = {
                "temperature": temperature or self.temperature,
                "max_output_tokens": max_tokens or self.max_tokens,
            }
            print(f"⚙️  Using temperature: {generation_config['temperature']}")

            # Generate response
            print("⏳ Waiting for Gemini response...")
            response = self.gemini_model.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            print(f"✅ Received response from Gemini ({len(response.text)} characters)")
            return response.text

        except Exception as e:
            print(f"❌ ERROR: Gemini failed to generate response")
            print(f"ℹ️  Error details: {str(e)}")
            print("ℹ️  POSSIBLE CAUSES:")
            print("   1. API key is invalid or expired")
            print("   2. Rate limit exceeded (60 requests/minute on free tier)")
            print("   3. Network connection issue")
            print("   4. Prompt contains blocked content")
            print("ℹ️  ACTION: Check error details above and try again")
            logger.error(f"Gemini generation error: {e}")
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
Your role is to explain placement recommendations in clear, actionable language that business stakeholders can understand.

Focus on:
- WHY this placement works (data-driven reasoning)
- Key success factors (traffic, visibility, category fit)
- Risk factors and considerations
- Competitive positioning
- Expected outcomes

Be concise but comprehensive. Use business terminology."""

        user_prompt = f"""Analyze this product placement recommendation:

**Product:**
- Name: {product['name']}
- Category: {product['category']}
- Price: ${product['price']:.2f}
- Price Tier: {product.get('price_tier', 'unknown')}

**Recommended Location:**
- Name: {location['zone_name']}
- Type: {location['zone_type']}
- Traffic Level: {location['traffic_level']} ({location['traffic_index']} daily visitors)
- Visibility Factor: {location['visibility_factor']}x
- Primary Category: {location['primary_category']}

**Predicted Performance:**
- ROI: {roi_score:.2f}x (${(roi_score - 1) * 100:.0f}% return)
- Estimated Placement Cost: ${location['base_placement_cost'] * 4:.0f}/month

**Additional Context:**
{json.dumps(context, indent=2) if context else 'No additional context'}

Provide a clear, strategic explanation of why this placement is optimal and what factors drive its success."""

        return self.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7
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
        context: Dict[str, Any]
    ) -> str:
        """
        Answer follow-up questions about recommendations using LLM.

        Args:
            question: User's question
            product: Product details
            recommendations: ROI recommendations
            context: Additional context (competitors, historical data, etc.)

        Returns:
            Natural language answer
        """
        system_prompt = """You are a retail analytics expert assistant helping stakeholders understand product placement recommendations.

Answer questions:
- Clearly and directly
- With data-driven reasoning
- Using specific numbers from the analysis
- In business-friendly language
- With actionable insights

If you don't have enough information, say so and explain what additional data would help."""

        recommendations_text = "\n".join([
            f"- {loc}: ROI {roi:.2f}"
            for loc, roi in list(recommendations.items())[:5]
        ])

        user_prompt = f"""Answer this question about our product placement analysis:

**Question:** {question}

**Product:** {product['name']} (${product['price']:.2f}, {product['category']})

**Our Recommendations:**
{recommendations_text}

**Available Context:**
{json.dumps(context, indent=2) if context else 'Limited context available'}

Provide a clear, helpful answer."""

        return self.generate(
            prompt=user_prompt,
            system_prompt=system_prompt,
            temperature=0.7
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
        base_url = None
        model = "gpt-4o-mini"  # Fast, cheap, good quality

        # Use OpenRouter if available
        if os.getenv('OPENROUTER_API_KEY'):
            base_url = "https://openrouter.ai/api/v1"
            model = "anthropic/claude-3.5-sonnet"  # Or any OpenRouter model

        _llm_client = LLMClient(
            api_key=api_key,
            base_url=base_url,
            model=model,
            temperature=0.7
        )

    return _llm_client


def set_llm_client(client: LLMClient):
    """Set global LLM client instance."""
    global _llm_client
    _llm_client = client
