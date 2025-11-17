"""
Sentiment Analysis and Emotion Detection
"""

from transformers import pipeline
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class SentimentAnalyzer:
    """Analyzes sentiment and detects emotions from text"""

    def __init__(self):
        """Initialize sentiment analyzer with DistilBERT"""
        try:
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model="distilbert-base-uncased-finetuned-sst-2-english"
            )
            logger.info("✅ Sentiment analyzer initialized")
        except Exception as e:
            logger.error(f"❌ Error initializing sentiment analyzer: {e}")
            self.sentiment_pipeline = None

    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment and map to game emotions

        Args:
            text: User message to analyze

        Returns:
            Dict with sentiment, confidence, emotion, and intensity
        """
        if not self.sentiment_pipeline:
            return self._fallback_analysis(text)

        try:
            result = self.sentiment_pipeline(text)[0]
            sentiment = result['label']
            confidence = result['score']

            # Map to game emotions
            emotion_mapping = {
                ('POSITIVE', lambda c: c > 0.9): 'excited',
                ('POSITIVE', lambda c: c > 0.7): 'satisfied',
                ('POSITIVE', lambda c: True): 'confident',
                ('NEGATIVE', lambda c: c > 0.9): 'frustrated',
                ('NEGATIVE', lambda c: c > 0.7): 'concerned',
                ('NEGATIVE', lambda c: True): 'disappointed',
            }

            emotion = 'curious'
            for (sent, condition), emo in emotion_mapping:
                if sentiment == sent and condition(confidence):
                    emotion = emo
                    break

            return {
                'sentiment': sentiment,
                'confidence': float(confidence),
                'emotion': emotion,
                'intensity': self._calculate_intensity(confidence),
                'raw_score': float(confidence)
            }
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return self._fallback_analysis(text)

    def _fallback_analysis(self, text: str) -> Dict:
        """Fallback keyword-based sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'perfect', 'wonderful', 'yes', 'okay', 'fine']
        negative_words = ['bad', 'terrible', 'awful', 'no', 'hate', 'expensive', 'sorry', 'disappointed']

        text_lower = text.lower()

        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            sentiment = 'POSITIVE'
            confidence = 0.7
            emotion = 'satisfied'
        elif negative_count > positive_count:
            sentiment = 'NEGATIVE'
            confidence = 0.7
            emotion = 'concerned'
        else:
            sentiment = 'NEUTRAL'
            confidence = 0.5
            emotion = 'curious'

        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'emotion': emotion,
            'intensity': self._calculate_intensity(confidence),
            'raw_score': confidence
        }

    @staticmethod
    def _calculate_intensity(confidence: float) -> str:
        """Calculate emotion intensity based on confidence"""
        if confidence > 0.85:
            return "strong"
        elif confidence > 0.7:
            return "moderate"
        else:
            return "mild"

class IntentClassifier:
    """Classifies user intent from message"""

    def __init__(self):
        """Initialize intent patterns"""
        self.intent_patterns = {
            'ask_price': ['how much', 'cost', 'price', 'expensive', 'cheap', 'affordable'],
            'ask_options': ['options', 'available', 'show', 'what', 'display', 'list'],
            'negotiate': ['discount', 'lower', 'reduce', 'too expensive', 'negotiate', 'offer'],
            'ask_data': ['data', 'analytics', 'statistics', 'roi', 'numbers', 'metrics', 'analysis'],
            'accept': ['yes', 'okay', 'accept', 'deal', 'agree', 'perfect', 'great', 'ok'],
            'reject': ['no', 'reject', 'not', 'cannot', 'never', 'hate', 'bad'],
            'ask_recommendation': ['recommend', 'suggest', 'advice', 'best', 'optimal'],
            'ask_explanation': ['why', 'explain', 'reason', 'because', 'how', 'works'],
            'general_query': []
        }

    def classify(self, text: str) -> Dict:
        """
        Classify intent from user message

        Args:
            text: User message

        Returns:
            Dict with primary and secondary intents and confidence
        """
        text_lower = text.lower()
        intent_scores = {}

        for intent, keywords in self.intent_patterns.items():
            if not keywords:
                intent_scores[intent] = 0
                continue

            matches = sum(1 for keyword in keywords if keyword in text_lower)
            score = matches / len(keywords) if keywords else 0
            intent_scores[intent] = score

        # Sort by score
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1], reverse=True)

        primary_intent = sorted_intents[0][0] if sorted_intents[0][1] > 0 else 'general_query'
        primary_confidence = sorted_intents[0][1]

        secondary_intent = sorted_intents[1][0] if len(sorted_intents) > 1 else None

        return {
            'primary': primary_intent,
            'confidence': primary_confidence,
            'secondary': secondary_intent,
            'all_scores': {intent: float(score) for intent, score in sorted_intents}
        }