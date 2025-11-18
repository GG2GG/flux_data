"""
Knowledge Base Loader - Loads and provides access to retail psychology research.

Provides research-backed insights from academic and industry sources to enrich
LLM responses with factual, cited information.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ResearchSource:
    """Represents a single research source."""
    id: str
    title: str
    url: str
    publisher: str
    year: int
    key_findings: List[str]
    data_points: Dict[str, float]

    def to_text(self) -> str:
        """Convert to readable text for LLM context."""
        findings = "\n  - ".join(self.key_findings)
        return f"{self.title} ({self.publisher}, {self.year}):\n  - {findings}"


class KnowledgeBaseLoader:
    """
    Loads and manages retail psychology knowledge base.

    Features:
    - Load research sources from JSON
    - Filter by topic/keyword
    - Get relevant citations
    - Extract data points for calculations
    """

    def __init__(self, kb_path: str = "knowledge_base/retail_psychology_sources.json"):
        """
        Initialize knowledge base loader.

        Args:
            kb_path: Path to knowledge base JSON file
        """
        self.kb_path = Path(kb_path)
        self.sources: List[ResearchSource] = []
        self.metadata: Dict[str, Any] = {}
        self._load_knowledge_base()

    def _load_knowledge_base(self):
        """Load knowledge base from JSON file."""
        if not self.kb_path.exists():
            logger.warning(f"Knowledge base not found: {self.kb_path}")
            return

        try:
            with open(self.kb_path, 'r') as f:
                data = json.load(f)

            self.metadata = data.get('metadata', {})

            # Parse sources
            for source_data in data.get('sources', []):
                source = ResearchSource(
                    id=source_data.get('id', ''),
                    title=source_data.get('title', ''),
                    url=source_data.get('url', ''),
                    publisher=source_data.get('publisher', ''),
                    year=source_data.get('year', 2024),
                    key_findings=source_data.get('key_findings', []),
                    data_points=source_data.get('data_points', {})
                )
                self.sources.append(source)

            logger.info(f"✓ Loaded {len(self.sources)} research sources from knowledge base")

        except Exception as e:
            logger.error(f"Failed to load knowledge base: {e}")

    def get_all_sources(self) -> List[ResearchSource]:
        """Get all research sources."""
        return self.sources

    def search_by_keyword(self, keyword: str) -> List[ResearchSource]:
        """
        Search sources by keyword in title or findings.

        Args:
            keyword: Search term (case-insensitive)

        Returns:
            List of matching sources
        """
        keyword_lower = keyword.lower()
        matches = []

        for source in self.sources:
            # Search in title
            if keyword_lower in source.title.lower():
                matches.append(source)
                continue

            # Search in findings
            for finding in source.key_findings:
                if keyword_lower in finding.lower():
                    matches.append(source)
                    break

        return matches

    def get_relevant_for_question(self, question: str, max_sources: int = 5) -> List[ResearchSource]:
        """
        Get relevant sources for a user question.

        Args:
            question: User's question
            max_sources: Maximum number of sources to return

        Returns:
            List of relevant sources
        """
        question_lower = question.lower()

        # Keywords that map to topics
        topic_keywords = {
            'eye level': ['eye level', 'eye-level', 'eye_level'],
            'endcap': ['endcap', 'end cap', 'end-cap'],
            'checkout': ['checkout', 'check-out', 'check out', 'impulse'],
            'traffic': ['traffic', 'foot traffic', 'footfall', 'visitor'],
            'placement': ['placement', 'positioning', 'location'],
            'shelf': ['shelf', 'shelving'],
            'psychology': ['psychology', 'behavior', 'behaviour', 'decision'],
            'sales': ['sales', 'revenue', 'performance'],
            'visibility': ['visibility', 'visible', 'sight', 'view'],
            'cost': ['cost', 'price', 'fee', 'pricing', 'investment']
        }

        # Find matching topics
        relevant_sources = []
        for topic, keywords in topic_keywords.items():
            for keyword in keywords:
                if keyword in question_lower:
                    # Search for sources about this topic
                    matches = self.search_by_keyword(topic)
                    relevant_sources.extend(matches)
                    break

        # Remove duplicates (keep first occurrence)
        seen_ids = set()
        unique_sources = []
        for source in relevant_sources:
            if source.id not in seen_ids:
                unique_sources.append(source)
                seen_ids.add(source.id)

        # If no specific matches, return general retail sources
        if not unique_sources:
            unique_sources = self.sources[:max_sources]

        return unique_sources[:max_sources]

    def get_data_point(self, key: str) -> Optional[float]:
        """
        Get a specific data point from any source.

        Args:
            key: Data point key (e.g., 'eye_level_sales_boost')

        Returns:
            First matching data point value, or None
        """
        for source in self.sources:
            if key in source.data_points:
                return source.data_points[key]
        return None

    def get_context_for_llm(
        self,
        question: str,
        max_sources: int = 3,
        include_citations: bool = True
    ) -> str:
        """
        Generate context string for LLM based on question.

        Args:
            question: User's question
            max_sources: Maximum number of sources to include
            include_citations: Whether to include URLs

        Returns:
            Formatted context string with research findings
        """
        sources = self.get_relevant_for_question(question, max_sources)

        if not sources:
            return ""

        context = "**Research-Backed Insights:**\n\n"

        for i, source in enumerate(sources, 1):
            context += f"{i}. **{source.title}** ({source.publisher}, {source.year})\n"
            for finding in source.key_findings[:3]:  # Top 3 findings
                context += f"   - {finding}\n"

            if include_citations:
                context += f"   - Source: {source.url}\n"

            context += "\n"

        return context

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics about the knowledge base."""
        total_findings = sum(len(s.key_findings) for s in self.sources)
        total_data_points = sum(len(s.data_points) for s in self.sources)

        publishers = set(s.publisher for s in self.sources)
        years = [s.year for s in self.sources]

        return {
            'total_sources': len(self.sources),
            'total_findings': total_findings,
            'total_data_points': total_data_points,
            'unique_publishers': len(publishers),
            'year_range': (min(years), max(years)) if years else (None, None),
            'publishers': sorted(list(publishers))
        }


# Global knowledge base instance
_global_kb: Optional[KnowledgeBaseLoader] = None


def get_knowledge_base() -> KnowledgeBaseLoader:
    """
    Get global knowledge base instance.

    Returns:
        KnowledgeBaseLoader instance
    """
    global _global_kb
    if _global_kb is None:
        _global_kb = KnowledgeBaseLoader()
    return _global_kb


def init_knowledge_base(kb_path: str = "knowledge_base/retail_psychology_sources.json") -> KnowledgeBaseLoader:
    """
    Initialize global knowledge base.

    Args:
        kb_path: Path to knowledge base JSON

    Returns:
        KnowledgeBaseLoader instance
    """
    global _global_kb
    _global_kb = KnowledgeBaseLoader(kb_path=kb_path)
    return _global_kb


if __name__ == '__main__':
    # Test the knowledge base loader
    logging.basicConfig(level=logging.INFO)

    kb = KnowledgeBaseLoader()

    print("\n" + "=" * 60)
    print("KNOWLEDGE BASE TEST")
    print("=" * 60)

    # Summary
    stats = kb.get_summary_statistics()
    print(f"\nTotal Sources: {stats['total_sources']}")
    print(f"Total Findings: {stats['total_findings']}")
    print(f"Year Range: {stats['year_range'][0]}-{stats['year_range'][1]}")

    # Test search
    print("\n" + "=" * 60)
    print("SEARCH TEST: 'eye level'")
    print("=" * 60)

    results = kb.search_by_keyword('eye level')
    print(f"Found {len(results)} sources")
    for source in results[:3]:
        print(f"\n- {source.title}")
        print(f"  {source.key_findings[0]}")

    # Test context generation
    print("\n" + "=" * 60)
    print("CONTEXT TEST: 'Why is eye level important?'")
    print("=" * 60)

    context = kb.get_context_for_llm("Why is eye level important?", max_sources=2)
    print(context)
