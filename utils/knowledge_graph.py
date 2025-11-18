"""
Knowledge Graph for Retail Placement Intelligence
Stores and queries research-backed knowledge about retail placement strategies
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import networkx as nx

logger = logging.getLogger(__name__)


class RetailKnowledgeGraph:
    """
    Knowledge graph for retail placement intelligence.

    Stores relationships between:
    - Products and categories
    - Locations and zones
    - Placement strategies and outcomes
    - Customer behaviors and preferences
    - Competitor insights
    """

    def __init__(self, knowledge_file: Optional[str] = None):
        """
        Initialize knowledge graph.

        Args:
            knowledge_file: Path to knowledge graph JSON file
        """
        self.graph = nx.DiGraph()  # Directed graph for causal relationships
        self.knowledge_file = knowledge_file

        if knowledge_file and Path(knowledge_file).exists():
            self.load_from_file(knowledge_file)
            logger.info(f"Loaded knowledge graph with {self.graph.number_of_nodes()} nodes")
        else:
            logger.info("Initialized empty knowledge graph")

    def add_concept(
        self,
        concept_id: str,
        concept_type: str,
        properties: Dict[str, Any]
    ) -> None:
        """
        Add a concept (node) to the knowledge graph.

        Args:
            concept_id: Unique identifier for concept
            concept_type: Type of concept (product, location, strategy, etc.)
            properties: Additional properties of the concept
        """
        self.graph.add_node(
            concept_id,
            type=concept_type,
            **properties
        )

    def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: str,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a relationship (edge) between two concepts.

        Args:
            source_id: Source concept ID
            target_id: Target concept ID
            relationship_type: Type of relationship (causes, requires, benefits, etc.)
            properties: Additional properties of the relationship
        """
        edge_props = {"type": relationship_type}
        if properties:
            edge_props.update(properties)

        self.graph.add_edge(source_id, target_id, **edge_props)

    def query_related_concepts(
        self,
        concept_id: str,
        relationship_type: Optional[str] = None,
        max_depth: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Query concepts related to a given concept.

        Args:
            concept_id: Starting concept ID
            relationship_type: Filter by relationship type (optional)
            max_depth: Maximum depth for traversal

        Returns:
            List of related concepts with relationship info
        """
        if concept_id not in self.graph:
            return []

        related = []

        # BFS traversal
        visited = {concept_id}
        queue = [(concept_id, 0)]  # (node, depth)

        while queue:
            current, depth = queue.pop(0)

            if depth >= max_depth:
                continue

            # Get outgoing edges
            for neighbor in self.graph.successors(current):
                edge_data = self.graph[current][neighbor]

                # Filter by relationship type if specified
                if relationship_type and edge_data.get('type') != relationship_type:
                    continue

                if neighbor not in visited:
                    visited.add(neighbor)
                    node_data = self.graph.nodes[neighbor]

                    related.append({
                        'concept_id': neighbor,
                        'type': node_data.get('type'),
                        'properties': {k: v for k, v in node_data.items() if k != 'type'},
                        'relationship': edge_data.get('type'),
                        'relationship_props': {k: v for k, v in edge_data.items() if k != 'type'},
                        'depth': depth + 1
                    })

                    queue.append((neighbor, depth + 1))

        return related

    def query_by_type(self, concept_type: str) -> List[Dict[str, Any]]:
        """
        Query all concepts of a given type.

        Args:
            concept_type: Type of concept to query

        Returns:
            List of concepts
        """
        results = []
        for node, data in self.graph.nodes(data=True):
            if data.get('type') == concept_type:
                results.append({
                    'concept_id': node,
                    'properties': {k: v for k, v in data.items() if k != 'type'}
                })
        return results

    def query_strategies_for_product(
        self,
        category: str,
        price_tier: str,
        target_customer: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Query placement strategies suitable for a product.

        Args:
            category: Product category
            price_tier: Price tier (budget, mid, premium)
            target_customer: Target customer segment (optional)

        Returns:
            List of recommended strategies with reasoning
        """
        strategies = []

        # Find product concept
        product_concepts = [
            node for node, data in self.graph.nodes(data=True)
            if data.get('type') == 'product_type' and
            data.get('category') == category and
            data.get('price_tier') == price_tier
        ]

        for product_concept in product_concepts:
            # Find strategies linked to this product type
            related = self.query_related_concepts(
                product_concept,
                relationship_type='benefits_from',
                max_depth=2
            )

            for item in related:
                if item['type'] == 'strategy':
                    strategies.append(item)

        return strategies

    def query_location_insights(
        self,
        zone_type: str,
        category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Query insights about a location type.

        Args:
            zone_type: Type of zone (end_cap, checkout, eye_level, etc.)
            category: Product category for category-specific insights

        Returns:
            Insights about the location
        """
        # Find location concept
        location_nodes = [
            node for node, data in self.graph.nodes(data=True)
            if data.get('type') == 'location_type' and
            data.get('zone_type') == zone_type
        ]

        if not location_nodes:
            return {}

        location_node = location_nodes[0]
        node_data = self.graph.nodes[location_node]

        # Get related insights
        related = self.query_related_concepts(location_node, max_depth=2)

        insights = {
            'zone_type': zone_type,
            'properties': {k: v for k, v in node_data.items() if k not in ['type', 'zone_type']},
            'best_for_categories': [],
            'strategies': [],
            'customer_behaviors': []
        }

        for item in related:
            if item['type'] == 'product_type':
                insights['best_for_categories'].append({
                    'category': item['properties'].get('category'),
                    'reason': item['relationship_props'].get('reason', '')
                })
            elif item['type'] == 'strategy':
                insights['strategies'].append({
                    'strategy': item['properties'].get('name'),
                    'description': item['properties'].get('description', '')
                })
            elif item['type'] == 'customer_behavior':
                insights['customer_behaviors'].append({
                    'behavior': item['properties'].get('name'),
                    'impact': item['properties'].get('impact', '')
                })

        return insights

    def save_to_file(self, filepath: str) -> None:
        """Save knowledge graph to JSON file."""
        data = {
            'nodes': [
                {'id': node, **data}
                for node, data in self.graph.nodes(data=True)
            ],
            'edges': [
                {'source': u, 'target': v, **data}
                for u, v, data in self.graph.edges(data=True)
            ]
        }

        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)

        logger.info(f"Saved knowledge graph to {filepath}")

    def load_from_file(self, filepath: str) -> None:
        """Load knowledge graph from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        # Add nodes
        for node in data['nodes']:
            node_id = node.pop('id')
            self.graph.add_node(node_id, **node)

        # Add edges
        for edge in data['edges']:
            source = edge.pop('source')
            target = edge.pop('target')
            self.graph.add_edge(source, target, **edge)

        logger.info(f"Loaded knowledge graph from {filepath}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph."""
        types_count = {}
        for _, data in self.graph.nodes(data=True):
            node_type = data.get('type', 'unknown')
            types_count[node_type] = types_count.get(node_type, 0) + 1

        relationship_types = {}
        for _, _, data in self.graph.edges(data=True):
            rel_type = data.get('type', 'unknown')
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1

        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_types': types_count,
            'relationship_types': relationship_types,
            'density': nx.density(self.graph),
            'average_degree': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes() if self.graph.number_of_nodes() > 0 else 0
        }


# Initialize global knowledge graph
_global_kg = None


def get_knowledge_graph() -> RetailKnowledgeGraph:
    """Get or create global knowledge graph instance."""
    global _global_kg
    if _global_kg is None:
        kg_path = Path(__file__).parent.parent / "data" / "knowledge_graph.json"
        _global_kg = RetailKnowledgeGraph(str(kg_path) if kg_path.exists() else None)
    return _global_kg
