"""
Utility functions for Neo4j GDS Community Detection Demo
=========================================================

This module provides helper utilities for:
- Connection management with environment variable support
- Data loading with idempotent operations
- Result export to CSV
- Logging configuration
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from graphdatascience import GraphDataScience
import pandas as pd


class Neo4jSessionManager:
    """
    Manages Neo4j connections with secure credential handling.

    Reads connection parameters from environment variables or CLI arguments,
    ensuring no secrets are hardcoded.

    Environment Variables:
        NEO4J_URI: Database URI (default: bolt://localhost:7687)
        NEO4J_USER: Username (default: neo4j)
        NEO4J_PASSWORD: Password (required)
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None
    ):
        """
        Initialize Neo4j connection manager.

        Args:
            uri: Neo4j URI (overrides NEO4J_URI env var)
            user: Username (overrides NEO4J_USER env var)
            password: Password (overrides NEO4J_PASSWORD env var)

        Raises:
            ValueError: If password is not provided via args or environment
        """
        self.uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
        self.user = user or os.getenv('NEO4J_USER', 'neo4j')
        self.password = password or os.getenv('NEO4J_PASSWORD')

        if not self.password:
            raise ValueError(
                "Neo4j password must be provided via NEO4J_PASSWORD "
                "environment variable or password argument"
            )

        self.gds: Optional[GraphDataScience] = None
        self.logger = logging.getLogger(__name__)

    def connect(self) -> GraphDataScience:
        """
        Establish connection to Neo4j and verify GDS availability.

        Returns:
            GraphDataScience client instance

        Raises:
            ConnectionError: If unable to connect or GDS is not available
        """
        try:
            self.logger.info(f"Connecting to Neo4j at {self.uri}")
            self.gds = GraphDataScience(self.uri, auth=(self.user, self.password))

            # Verify connection and GDS version
            version = self.gds.version()
            self.logger.info(f"Successfully connected. GDS Version: {version}")

            return self.gds

        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {e}")
            raise ConnectionError(
                f"Unable to connect to Neo4j at {self.uri}. "
                "Ensure Neo4j is running and credentials are correct."
            ) from e

    def close(self):
        """Close the Neo4j connection."""
        if self.gds:
            self.logger.info("Closing Neo4j connection")
            # GDS client doesn't have explicit close, but we can set to None
            self.gds = None


class DataLoader:
    """
    Handles idempotent data loading for the community detection demo.

    Ensures that data can be safely reloaded without duplication.
    """

    def __init__(self, gds: GraphDataScience):
        """
        Initialize data loader.

        Args:
            gds: Connected GraphDataScience client
        """
        self.gds = gds
        self.logger = logging.getLogger(__name__)

    def clear_existing_data(self):
        """Remove existing User nodes and relationships."""
        self.logger.info("Clearing existing data")
        cypher = "MATCH (n:User) DETACH DELETE n"
        self.gds.run_cypher(cypher)
        self.logger.info("Existing data cleared")

    def load_sample_data(self) -> Dict[str, int]:
        """
        Load sample social network data with idempotent MERGE operations.

        Creates a social network with 10 users divided into 3 communities
        with varying connection strengths.

        Returns:
            Dictionary with counts of created nodes and relationships
        """
        self.logger.info("Loading sample social network data")

        # First, clear any existing data to ensure idempotence
        self.clear_existing_data()

        # Create users and relationships
        cypher = """
        // Create users with MERGE for idempotence
        MERGE (alice:User {userId: 1}) ON CREATE SET alice.name = 'Alice'
        MERGE (bob:User {userId: 2}) ON CREATE SET bob.name = 'Bob'
        MERGE (carol:User {userId: 3}) ON CREATE SET carol.name = 'Carol'
        MERGE (david:User {userId: 4}) ON CREATE SET david.name = 'David'
        MERGE (eve:User {userId: 5}) ON CREATE SET eve.name = 'Eve'
        MERGE (frank:User {userId: 6}) ON CREATE SET frank.name = 'Frank'
        MERGE (grace:User {userId: 7}) ON CREATE SET grace.name = 'Grace'
        MERGE (henry:User {userId: 8}) ON CREATE SET henry.name = 'Henry'
        MERGE (iris:User {userId: 9}) ON CREATE SET iris.name = 'Iris'
        MERGE (jack:User {userId: 10}) ON CREATE SET jack.name = 'Jack'

        WITH 1 as dummy

        // Create FOLLOWS relationships with weights (interaction strength)
        // Community 1: Alice, Bob, Carol (tight-knit group)
        MATCH (alice:User {userId: 1}), (bob:User {userId: 2})
        MERGE (alice)-[:FOLLOWS {weight: 10}]->(bob)

        WITH 1 as dummy
        MATCH (bob:User {userId: 2}), (alice:User {userId: 1})
        MERGE (bob)-[:FOLLOWS {weight: 8}]->(alice)

        WITH 1 as dummy
        MATCH (alice:User {userId: 1}), (carol:User {userId: 3})
        MERGE (alice)-[:FOLLOWS {weight: 9}]->(carol)

        WITH 1 as dummy
        MATCH (carol:User {userId: 3}), (alice:User {userId: 1})
        MERGE (carol)-[:FOLLOWS {weight: 7}]->(alice)

        WITH 1 as dummy
        MATCH (bob:User {userId: 2}), (carol:User {userId: 3})
        MERGE (bob)-[:FOLLOWS {weight: 12}]->(carol)

        WITH 1 as dummy
        MATCH (carol:User {userId: 3}), (bob:User {userId: 2})
        MERGE (carol)-[:FOLLOWS {weight: 11}]->(bob)

        WITH 1 as dummy
        // Community 2: David, Eve, Frank (another tight-knit group)
        MATCH (david:User {userId: 4}), (eve:User {userId: 5})
        MERGE (david)-[:FOLLOWS {weight: 9}]->(eve)

        WITH 1 as dummy
        MATCH (eve:User {userId: 5}), (david:User {userId: 4})
        MERGE (eve)-[:FOLLOWS {weight: 8}]->(david)

        WITH 1 as dummy
        MATCH (david:User {userId: 4}), (frank:User {userId: 6})
        MERGE (david)-[:FOLLOWS {weight: 10}]->(frank)

        WITH 1 as dummy
        MATCH (frank:User {userId: 6}), (david:User {userId: 4})
        MERGE (frank)-[:FOLLOWS {weight: 9}]->(david)

        WITH 1 as dummy
        MATCH (eve:User {userId: 5}), (frank:User {userId: 6})
        MERGE (eve)-[:FOLLOWS {weight: 11}]->(frank)

        WITH 1 as dummy
        MATCH (frank:User {userId: 6}), (eve:User {userId: 5})
        MERGE (frank)-[:FOLLOWS {weight: 10}]->(eve)

        WITH 1 as dummy
        // Community 3: Grace, Henry, Iris (loose group)
        MATCH (grace:User {userId: 7}), (henry:User {userId: 8})
        MERGE (grace)-[:FOLLOWS {weight: 5}]->(henry)

        WITH 1 as dummy
        MATCH (henry:User {userId: 8}), (iris:User {userId: 9})
        MERGE (henry)-[:FOLLOWS {weight: 4}]->(iris)

        WITH 1 as dummy
        MATCH (iris:User {userId: 9}), (grace:User {userId: 7})
        MERGE (iris)-[:FOLLOWS {weight: 3}]->(grace)

        WITH 1 as dummy
        // Bridge connections (weak ties between communities)
        MATCH (carol:User {userId: 3}), (david:User {userId: 4})
        MERGE (carol)-[:FOLLOWS {weight: 2}]->(david)

        WITH 1 as dummy
        MATCH (frank:User {userId: 6}), (grace:User {userId: 7})
        MERGE (frank)-[:FOLLOWS {weight: 1}]->(grace)

        WITH 1 as dummy
        MATCH (jack:User {userId: 10}), (alice:User {userId: 1})
        MERGE (jack)-[:FOLLOWS {weight: 1}]->(alice)

        WITH 1 as dummy
        MATCH (jack:User {userId: 10}), (grace:User {userId: 7})
        MERGE (jack)-[:FOLLOWS {weight: 1}]->(grace)

        WITH 1 as dummy
        // Count results
        MATCH (u:User)
        WITH count(u) as nodeCount
        MATCH ()-[r:FOLLOWS]->()
        RETURN nodeCount, count(r) as relationshipCount
        """

        result = self.gds.run_cypher(cypher)

        stats = {
            'nodes': int(result.iloc[0]['nodeCount']),
            'relationships': int(result.iloc[0]['relationshipCount'])
        }

        self.logger.info(
            f"Data loaded successfully: {stats['nodes']} nodes, "
            f"{stats['relationships']} relationships"
        )

        return stats


class ResultExporter:
    """
    Exports community detection results to CSV files.
    """

    def __init__(self, output_dir: Path):
        """
        Initialize result exporter.

        Args:
            output_dir: Directory where CSV files will be saved
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

    def export_communities(
        self,
        community_data: pd.DataFrame,
        filename: str = "communities.csv"
    ):
        """
        Export community assignments to CSV.

        Args:
            community_data: DataFrame with nodeId and communityId columns
            filename: Output filename
        """
        output_path = self.output_dir / filename
        self.logger.info(f"Exporting community data to {output_path}")

        community_data.to_csv(output_path, index=False)
        self.logger.info(f"Community data exported successfully")

    def export_statistics(
        self,
        stats: Dict[str, Any],
        filename: str = "community_stats.csv"
    ):
        """
        Export community statistics to CSV.

        Args:
            stats: Dictionary of statistics
            filename: Output filename
        """
        output_path = self.output_dir / filename
        self.logger.info(f"Exporting statistics to {output_path}")

        # Convert dict to DataFrame
        stats_df = pd.DataFrame([stats])
        stats_df.to_csv(output_path, index=False)
        self.logger.info(f"Statistics exported successfully")

    def export_community_summary(
        self,
        community_data: pd.DataFrame,
        filename: str = "community_summary.csv"
    ):
        """
        Export community size summary to CSV.

        Args:
            community_data: DataFrame with communityId column
            filename: Output filename
        """
        output_path = self.output_dir / filename
        self.logger.info(f"Exporting community summary to {output_path}")

        summary = community_data.groupby('communityId').size().reset_index(name='member_count')
        summary = summary.sort_values('member_count', ascending=False)
        summary.to_csv(output_path, index=False)
        self.logger.info(f"Community summary exported successfully")


def setup_logging(level: str = "INFO") -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    logger = logging.getLogger(__name__)
    logger.info(f"Logging initialized at {level} level")

    return logger
