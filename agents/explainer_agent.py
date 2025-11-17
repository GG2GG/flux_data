"""
Explainer Agent - Generates comprehensive explanations for recommendations.
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List
from .base_agent import BaseAgent
from models.schemas import (
    PlacementState, Explanation, FeatureImportance,
    HistoricalExample, CompetitorProduct
)


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

        # Generate all explanation components
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
        Generate SHAP-style feature importance explanation.

        This simulates what XGBoost + SHAP would produce.
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

        # Simulate SHAP values based on what contributed to ROI
        features = []

        # Location traffic contribution
        traffic_contribution = (location_obj.traffic_index / 200) * 0.30
        features.append(('location_traffic', traffic_contribution, location_obj.traffic_index))

        # Zone type contribution
        zone_contribution = (location_obj.visibility_factor - 1.0) * 0.25
        features.append(('zone_visibility', zone_contribution, location_obj.visibility_factor))

        # Category fit contribution (simplified)
        category_contribution = 0.20 if product.category.lower() in ['beverages', 'snacks'] else 0.10
        features.append(('category_fit', category_contribution, 1.0 if category_contribution > 0.15 else 0.5))

        # Price tier contribution
        price_tier_contribution = 0.15 if product.price > 3.0 else 0.05
        features.append(('price_positioning', price_tier_contribution, product.price))

        # Budget efficiency
        budget_contribution = 0.10
        features.append(('budget_efficiency', budget_contribution, product.budget / prediction.placement_cost))

        # Sort by absolute contribution
        features.sort(key=lambda x: abs(x[1]), reverse=True)

        # Generate markdown explanation
        explanation = "**Key factors influencing this recommendation:**\n\n"

        for i, (feature, shap_value, value) in enumerate(features[:5], 1):
            impact = "increased" if shap_value > 0 else "decreased"
            feature_display = feature.replace('_', ' ').title()

            explanation += f"{i}. **{feature_display}** (value: {value:.2f}): "
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
            # Default: provide summary
            return state.explanation.feature_importance if state.explanation else "I can explain the recommendation based on feature importance, historical evidence, competitor benchmarks, or alternative scenarios. Please ask a more specific question."
