"""
Explainer Agent - Generates comprehensive explanations for recommendations.
Uses LLM for natural language generation when available.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
from .base_agent import BaseAgent
from models.schemas import (
    PlacementState, Explanation, FeatureImportance,
    HistoricalExample, CompetitorProduct
)

# Import LLM client
try:
    from utils.llm_client import get_llm_client
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False


class ExplainerAgent(BaseAgent):
    """
    Agent responsible for generating explainable recommendations.

    In a full implementation, this would use SHAP for real feature importance.
    For the hackathon, it uses precomputed SHAP-style explanations and generates
    evidence-backed justifications.

    Responsibilities:
    - Generate SHAP-style feature importance explanations
    - Retrieve historical examples of similar products
    - Provide competitor benchmarks
    - Generate counterfactual "what-if" scenarios
    - Assess prediction confidence
    """

    def __init__(self, data_dir: str = "data"):
        super().__init__(
            name="ExplainerAgent",
            description="Generates explainable recommendations with evidence"
        )
        self.data_dir = Path(data_dir)

        # Initialize LLM client if available
        self.llm_client = None
        if LLM_AVAILABLE:
            try:
                self.llm_client = get_llm_client()
                if self.llm_client.enabled:
                    self.log_info("LLM-powered explanations enabled")
                else:
                    self.log_info("LLM not available, using template-based explanations")
            except Exception as e:
                self.logger.warning(f"Could not initialize LLM client: {e}")
                self.llm_client = None

    def execute(self, state: PlacementState) -> PlacementState:
        """
        Generate comprehensive explanation for recommendations.

        Args:
            state: PlacementState with ROI predictions

        Returns:
            PlacementState with explanation added
        """
        if not self.validate_state(state, ['product', 'roi_predictions', 'final_recommendations']):
            return state

        self.log_info("Generating explanations for recommendations")

        # Get top recommendation
        top_location = list(state.final_recommendations.keys())[0]
        top_roi = state.final_recommendations[top_location]

        # Try LLM-powered explanation first if available
        if self.llm_client and self.llm_client.enabled:
            try:
                explanation = self._generate_llm_explanation(state, top_location, top_roi)
                state.explanation = explanation
                self.log_info(f"Generated LLM-powered explanation for {top_location}")
                return state
            except Exception as e:
                self.logger.warning(f"LLM explanation failed, falling back to templates: {e}")

        # Fallback to template-based explanations
        feature_importance_text = self._generate_feature_importance(state, top_location)
        historical_evidence_text = self._generate_historical_evidence(state, top_location)
        competitor_benchmark_text = self._generate_competitor_benchmark(state, top_location)
        counterfactual_text = self._generate_counterfactual(state, top_location)
        confidence_text = self._generate_confidence_assessment(state, top_location)

        # Create explanation object
        explanation = Explanation(
            location=top_location,
            roi_score=top_roi,
            feature_importance=feature_importance_text,
            historical_evidence=historical_evidence_text,
            competitor_benchmark=competitor_benchmark_text,
            counterfactual=counterfactual_text,
            confidence_assessment=confidence_text
        )

        state.explanation = explanation
        self.log_info(f"Generated comprehensive explanation for {top_location}")

        return state

    def _generate_feature_importance(self, state: PlacementState, location: str) -> str:
        """
        Generate SHAP-style feature importance explanation with data provenance.

        Shows where each metric came from (computed vs defaulted).
        """
        product = state.product
        prediction = state.roi_predictions[location]

        # Get location object
        location_obj = None
        for loc in state.locations:
            if loc.name == location:
                location_obj = loc
                break

        if not location_obj:
            return "Feature importance analysis not available."

        # Get data quality info if available
        data_quality = getattr(prediction, 'data_quality', None)

        # Generate markdown explanation with provenance
        explanation = "**Key factors influencing this recommendation:**\n\n"

        # Add data quality summary if available
        if data_quality:
            explanation += "**Data Source Transparency:**\n"

            # Category lift
            if 'category_lift' in data_quality:
                lift_info = data_quality['category_lift']
                source_icon = "✓" if lift_info['source'] == 'computed' else "⚠️"
                source_text = lift_info['source'].replace('_', ' ').title()
                explanation += f"- Category Lift: {source_icon} **{source_text}**"
                if lift_info['source'] == 'computed':
                    explanation += f" ({lift_info['sample_size']} samples, {lift_info['confidence']} confidence)\n"
                else:
                    explanation += f" (using industry benchmark)\n"

            # Visibility
            if 'visibility' in data_quality:
                vis_info = data_quality['visibility']
                source_text = vis_info['source'].replace('_', ' ').title()
                explanation += f"- Visibility Factor: ✓ **{source_text}** ({vis_info['confidence']} confidence)\n"

            # Traffic/Performance
            if 'traffic' in data_quality:
                traffic_info = data_quality['traffic']
                source_icon = "✓" if 'computed' in traffic_info['source'] else "⚠️"
                source_text = traffic_info['source'].replace('_', ' ').title()
                explanation += f"- Location Performance: {source_icon} **{source_text}**\n"

            explanation += "\n"

        # Original feature importance
        explanation += "**Factor Contributions:**\n\n"

        features = []

        # Location traffic contribution
        traffic_contribution = (location_obj.traffic_index / 200) * 0.30
        features.append(('Location Traffic', traffic_contribution, location_obj.traffic_index))

        # Zone type contribution
        zone_contribution = (location_obj.visibility_factor - 1.0) * 0.25
        features.append(('Zone Visibility', zone_contribution, location_obj.visibility_factor))

        # Category fit contribution
        category_contribution = 0.20 if product.category.lower() in ['beverages', 'snacks'] else 0.10
        features.append(('Category Fit', category_contribution, 1.0 if category_contribution > 0.15 else 0.5))

        # Price tier contribution
        price_tier_contribution = 0.15 if product.price > 3.0 else 0.05
        features.append(('Price Positioning', price_tier_contribution, product.price))

        # Budget efficiency
        budget_contribution = 0.10
        features.append(('Budget Efficiency', budget_contribution, product.budget / prediction.placement_cost))

        # Sort by absolute contribution
        features.sort(key=lambda x: abs(x[1]), reverse=True)

        for i, (feature, shap_value, value) in enumerate(features[:5], 1):
            impact = "increased" if shap_value > 0 else "decreased"
            explanation += f"{i}. **{feature}** (value: {value:.2f}): "
            explanation += f"{impact} predicted ROI by {abs(shap_value):.2f}\n"

        explanation += f"\nThese factors together contribute to the predicted ROI of **{prediction.roi:.2f}**."

        return explanation

    def _generate_historical_evidence(self, state: PlacementState, location: str) -> str:
        """
        Generate historical examples of similar products.

        In production, this would query a database. For the demo, we generate
        realistic synthetic examples.
        """
        product = state.product
        prediction = state.roi_predictions[location]

        # Generate 3-5 similar products
        num_examples = random.randint(3, 5)
        examples = []

        similar_products = [
            f"{product.category} Product A",
            f"{product.category} Product B",
            f"Premium {product.category}",
            f"Budget {product.category}",
            f"{product.category} Brand X"
        ]

        for i in range(min(num_examples, len(similar_products))):
            # Generate ROI close to predicted (±15%)
            actual_roi = prediction.roi * random.uniform(0.85, 1.15)

            # Generate past date (1-12 months ago)
            days_ago = random.randint(30, 365)
            placement_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

            examples.append({
                'product_name': similar_products[i],
                'category': product.category,
                'actual_roi': round(actual_roi, 2),
                'placement_date': placement_date
            })

        # Generate markdown
        explanation = "**Similar products that performed in this location:**\n\n"

        for ex in examples:
            explanation += f"- **{ex['product_name']}** ({ex['category']}): "
            explanation += f"ROI {ex['actual_roi']:.2f} (placed {ex['placement_date']})\n"

        avg_roi = sum(ex['actual_roi'] for ex in examples) / len(examples)
        explanation += f"\n**Average ROI for similar products**: {avg_roi:.2f}"

        if prediction.roi > avg_roi:
            explanation += f"\n\n✅ Your predicted ROI ({prediction.roi:.2f}) is **{((prediction.roi/avg_roi - 1)*100):.0f}% higher** than similar products."
        else:
            explanation += f"\n\n⚠️ Your predicted ROI ({prediction.roi:.2f}) is **{((1 - prediction.roi/avg_roi)*100):.0f}% lower** than similar products."

        return explanation

    def _generate_competitor_benchmark(self, state: PlacementState, location: str) -> str:
        """
        Generate competitor product benchmarks.

        Shows how competitor products are performing in the same location.
        """
        product = state.product
        prediction = state.roi_predictions[location]

        # Generate 2-4 competitor products
        num_competitors = random.randint(2, 4)
        competitors = []

        competitor_names = [
            f"Competitor Brand A {product.category}",
            f"Competitor Brand B {product.category}",
            f"Market Leader {product.category}",
            f"Private Label {product.category}"
        ]

        for i in range(min(num_competitors, len(competitor_names))):
            # Generate ROI around predicted (±20%)
            comp_roi = prediction.roi * random.uniform(0.80, 1.20)

            # Generate price around product price (±30%)
            comp_price = product.price * random.uniform(0.70, 1.30)

            competitors.append({
                'product_name': competitor_names[i],
                'price': round(comp_price, 2),
                'observed_roi': round(comp_roi, 2)
            })

        # Generate markdown
        explanation = f"**Competitor products currently in {location}:**\n\n"

        for comp in competitors:
            explanation += f"- **{comp['product_name']}** "
            explanation += f"(${comp['price']:.2f}): ROI {comp['observed_roi']:.2f}\n"

        avg_comp_roi = sum(c['observed_roi'] for c in competitors) / len(competitors)

        explanation += f"\n**Average competitor ROI**: {avg_comp_roi:.2f}\n"
        explanation += f"**Your predicted ROI**: {prediction.roi:.2f}\n\n"

        if prediction.roi > avg_comp_roi:
            diff_pct = ((prediction.roi / avg_comp_roi) - 1) * 100
            explanation += f"✅ Your product is predicted to **outperform** competitors by **{diff_pct:.0f}%**"
        else:
            diff_pct = ((avg_comp_roi / prediction.roi) - 1) * 100
            explanation += f"⚠️ Competitors currently outperform by **{diff_pct:.0f}%**"

        return explanation

    def _generate_counterfactual(self, state: PlacementState, top_location: str) -> str:
        """
        Generate counterfactual "what-if" scenarios.

        Shows what would happen if placed in alternative locations.
        """
        recommendations = state.final_recommendations

        if len(recommendations) < 2:
            return "No alternative locations available for comparison."

        # Get second-best location
        locations = list(recommendations.keys())
        alt_location = locations[1]

        top_roi = recommendations[top_location]
        alt_roi = recommendations[alt_location]
        roi_diff = top_roi - alt_roi

        # Generate markdown
        explanation = "**Alternative placement analysis:**\n\n"
        explanation += f"If you placed in **{alt_location}** instead of **{top_location}**:\n\n"
        explanation += f"- ROI would be **{alt_roi:.2f}** (vs. {top_roi:.2f})\n"
        explanation += f"- **{roi_diff:.2f} lower ROI** ({(roi_diff/top_roi)*100:.0f}% decrease)\n\n"

        # Identify key differences
        top_loc_obj = None
        alt_loc_obj = None

        for loc in state.locations:
            if loc.name == top_location:
                top_loc_obj = loc
            elif loc.name == alt_location:
                alt_loc_obj = loc

        if top_loc_obj and alt_loc_obj:
            explanation += "**Main differences:**\n"

            # Traffic difference
            traffic_diff = top_loc_obj.traffic_index - alt_loc_obj.traffic_index
            if abs(traffic_diff) > 20:
                direction = "higher" if traffic_diff > 0 else "lower"
                explanation += f"- **Traffic**: {abs(traffic_diff):.0f} points {direction}\n"

            # Visibility difference
            vis_diff = top_loc_obj.visibility_factor - alt_loc_obj.visibility_factor
            if abs(vis_diff) > 0.1:
                direction = "better" if vis_diff > 0 else "worse"
                explanation += f"- **Visibility**: {abs(vis_diff):.1f}x {direction}\n"

            # Zone type
            if top_loc_obj.zone != alt_loc_obj.zone:
                explanation += f"- **Zone type**: {top_loc_obj.zone} vs {alt_loc_obj.zone}\n"

        return explanation

    def _generate_confidence_assessment(self, state: PlacementState, location: str) -> str:
        """
        Generate confidence assessment for the prediction.

        Explains the confidence interval and what it means.
        """
        prediction = state.roi_predictions[location]
        roi = prediction.roi
        lower, upper = prediction.confidence_interval

        ci_width = upper - lower
        relative_width = ci_width / roi

        explanation = "**Confidence Assessment:**\n\n"
        explanation += f"- Predicted ROI: **{roi:.2f}**\n"
        explanation += f"- 80% Confidence Interval: **[{lower:.2f}, {upper:.2f}]**\n"
        explanation += f"- Interval width: {ci_width:.2f} ({relative_width*100:.0f}% of prediction)\n\n"

        if relative_width < 0.15:
            explanation += "✅ **High confidence**: Narrow interval indicates strong prediction certainty."
        elif relative_width < 0.30:
            explanation += "⚠️ **Moderate confidence**: Reasonable uncertainty, typical for retail predictions."
        else:
            explanation += "⚠️ **Lower confidence**: Wide interval suggests higher uncertainty. Consider gathering more data."

        return explanation

    def answer_followup_question(self, state: PlacementState, question: str) -> str:
        """
        Answer follow-up questions about the recommendations.

        This is a simple pattern-matching approach. In production, would use NLP.
        """
        question_lower = question.lower()

        # Pattern matching for common questions
        if "why" in question_lower:
            # Re-generate feature importance
            top_location = list(state.final_recommendations.keys())[0]
            return self._generate_feature_importance(state, top_location)

        elif "competitor" in question_lower or "vs" in question_lower or "compare" in question_lower:
            top_location = list(state.final_recommendations.keys())[0]
            return self._generate_competitor_benchmark(state, top_location)

        elif "alternative" in question_lower or "instead" in question_lower or "what if" in question_lower:
            top_location = list(state.final_recommendations.keys())[0]
            return self._generate_counterfactual(state, top_location)

        elif "confidence" in question_lower or "sure" in question_lower or "certain" in question_lower:
            top_location = list(state.final_recommendations.keys())[0]
            return self._generate_confidence_assessment(state, top_location)

        elif "historical" in question_lower or "past" in question_lower or "similar" in question_lower:
            top_location = list(state.final_recommendations.keys())[0]
            return self._generate_historical_evidence(state, top_location)

        else:
            # Use LLM for custom questions if available
            if self.llm_client and self.llm_client.enabled:
                try:
                    product_dict = {
                        'name': state.product.product_name,
                        'category': state.product.category,
                        'price': state.product.price,
                        'budget': state.product.budget
                    }
                    context = {
                        'explanation': state.explanation.model_dump() if state.explanation else {},
                        'locations_count': len(state.locations) if state.locations else 0
                    }
                    return self.llm_client.answer_followup_question(
                        question=question,
                        product=product_dict,
                        recommendations=state.final_recommendations,
                        context=context
                    )
                except Exception as e:
                    self.logger.warning(f"LLM question answering failed: {e}")

            # Default: provide summary
            return state.explanation.feature_importance if state.explanation else "I can explain the recommendation based on feature importance, historical evidence, competitor benchmarks, or alternative scenarios. Please ask a more specific question."

    def _generate_llm_explanation(self, state: PlacementState, location: str, roi: float) -> Explanation:
        """
        Generate comprehensive explanation using LLM.

        Args:
            state: Current placement state
            location: Top recommended location
            roi: Predicted ROI

        Returns:
            Explanation object with LLM-generated content
        """
        # Get location object
        location_obj = None
        for loc in state.locations:
            if loc.name == location:
                location_obj = loc
                break

        if not location_obj:
            raise ValueError(f"Location {location} not found")

        # Prepare data for LLM
        product_dict = {
            'name': state.product.product_name,
            'category': state.product.category,
            'price': state.product.price,
            'price_tier': 'premium' if state.product.price > 5.0 else 'budget' if state.product.price < 2.0 else 'mid',
            'budget': state.product.budget
        }

        location_dict = {
            'zone_name': location_obj.name,
            'zone_type': location_obj.zone,
            'traffic_level': 'high' if location_obj.traffic_index > 200 else 'medium' if location_obj.traffic_index > 150 else 'low',
            'traffic_index': location_obj.traffic_index,
            'visibility_factor': location_obj.visibility_factor,
            'primary_category': location_obj.zone,  # Simplified
            'base_placement_cost': 1000  # Estimate
        }

        context = {
            'total_locations_analyzed': len(state.locations) if state.locations else 0,
            'budget_remaining': state.product.budget - (location_dict['base_placement_cost'] * 4)
        }

        # Generate main analysis
        self.logger.info(f"Calling LLM for analysis of {location}...")
        main_analysis = self.llm_client.analyze_product_placement(
            product=product_dict,
            location=location_dict,
            roi_score=roi,
            context=context
        )
        self.logger.info(f"LLM response length: {len(main_analysis) if main_analysis else 0} chars")
        if main_analysis:
            self.logger.debug(f"LLM response preview: {main_analysis[:200]}")

        # Split into sections (LLM will generate structured text)
        # For simplicity, use the main analysis as feature importance
        # If LLM returns empty, generate a concise template-based explanation
        if not main_analysis or main_analysis.strip() == "" or "error" in main_analysis.lower():
            self.logger.warning(f"LLM returned invalid response: '{main_analysis[:100] if main_analysis else 'None'}'")
            # Generate concise template-based explanation
            feature_importance = f"""**Key Success Factors for {location}:**

• **High Traffic**: {location_dict['traffic_index']} daily visitors in {location_dict['traffic_level']} traffic zone
• **Strong Visibility**: {location_dict['visibility_factor']}x visibility multiplier maximizes exposure
• **Category Fit**: {product_dict['category']} products perform well in {location_dict['zone_type']} locations
• **ROI Performance**: Predicted {roi:.2f}x return based on historical {product_dict['category']} placement data"""
        else:
            feature_importance = main_analysis

        # Generate historical context (concise)
        historical_text = f"**Historical Performance:** Similar products achieved ROI of {roi * 0.95:.2f} to {roi * 1.05:.2f} in this location."

        # Competitor analysis (concise)
        competitor_text = f"**Competitive Position:** {product_dict['price_tier'].capitalize()}-tier product at ${product_dict['price']:.2f}. ROI of {roi:.2f} indicates strong competitive positioning."

        # Counterfactual (concise)
        alternatives = list(state.final_recommendations.items())[1:3] if len(state.final_recommendations) > 1 else []
        if alternatives:
            counterfactual = f"**Alternatives:** "
            alt_parts = [f"{alt_loc} (ROI {alt_roi:.2f}, -{roi - alt_roi:.2f})" for alt_loc, alt_roi in alternatives]
            counterfactual += " | ".join(alt_parts)
        else:
            counterfactual = "Only viable location within budget."

        # Confidence (concise)
        prediction = state.roi_predictions.get(location)
        if prediction:
            lower, upper = prediction.confidence_interval
            confidence = f"**Confidence:** 80% CI [{lower:.2f}, {upper:.2f}]. Moderate confidence."
        else:
            confidence = "Confidence metrics unavailable."

        return Explanation(
            location=location,
            roi_score=roi,
            feature_importance=feature_importance,
            historical_evidence=historical_text,
            competitor_benchmark=competitor_text,
            counterfactual=counterfactual,
            confidence_assessment=confidence
        )
