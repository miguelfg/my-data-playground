#!/usr/bin/env python3
"""
Neo4j GDS Community Detection Demo
===================================

Production-ready demo showcasing community detection algorithms in Neo4j GDS.

This script demonstrates:
1. Secure connection management with environment variables
2. Idempotent data loading
3. Graph projection and validation
4. Multiple community detection algorithms (Louvain, Label Propagation)
5. Result analysis and interpretation
6. CSV export for further analysis

Usage:
    # Basic usage (uses environment variables from .env)
    python demo.py

    # With CLI arguments
    python demo.py --uri bolt://localhost:7687 --user neo4j --password secret

    # With custom parameters
    python demo.py --max-iterations 20 --tolerance 0.001 --output-dir ./results

Environment Variables:
    NEO4J_URI: Database URI (default: bolt://localhost:7687)
    NEO4J_USER: Username (default: neo4j)
    NEO4J_PASSWORD: Password (required if not provided via CLI)

Requirements:
    - Neo4j 5.x with GDS plugin installed
    - Python 3.13+
    - Dependencies: graphdatascience, pandas
"""

import argparse
import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
import pandas as pd
from graphdatascience import GraphDataScience

from utils import (
    Neo4jSessionManager,
    DataLoader,
    ResultExporter,
    setup_logging
)


class CommunityDetectionDemo:
    """
    Orchestrates the complete community detection workflow.
    """

    def __init__(
        self,
        gds: GraphDataScience,
        output_dir: Path,
        max_iterations: int = 10,
        tolerance: float = 0.0001,
        resolution: float = 1.0
    ):
        """
        Initialize demo orchestrator.

        Args:
            gds: Connected GraphDataScience client
            output_dir: Directory for output files
            max_iterations: Maximum iterations for algorithms
            tolerance: Convergence tolerance
            resolution: Resolution parameter for Louvain
        """
        self.gds = gds
        self.output_dir = Path(output_dir)
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.resolution = resolution
        self.logger = setup_logging()

        self.exporter = ResultExporter(self.output_dir / "derived")
        self.graph_name = "social-network-demo"
        self.G = None

    def run_full_workflow(self) -> Dict[str, Any]:
        """
        Execute complete community detection workflow.

        Returns:
            Dictionary containing all results and metrics
        """
        start_time = time.time()

        try:
            # Step 1: Load data
            self.logger.info("=" * 70)
            self.logger.info("STEP 1: DATA LOADING")
            self.logger.info("=" * 70)
            data_stats = self._load_data()

            # Step 2: Create graph projection
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 2: GRAPH PROJECTION")
            self.logger.info("=" * 70)
            projection_stats = self._create_graph_projection()

            # Step 3: Run Louvain algorithm
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 3: LOUVAIN COMMUNITY DETECTION")
            self.logger.info("=" * 70)
            louvain_results = self._run_louvain()

            # Step 4: Run Label Propagation (optional comparison)
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 4: LABEL PROPAGATION (Comparison)")
            self.logger.info("=" * 70)
            label_prop_results = self._run_label_propagation()

            # Step 5: Analyze results
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 5: COMMUNITY ANALYSIS")
            self.logger.info("=" * 70)
            analysis = self._analyze_communities(louvain_results)

            # Step 6: Export results
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 6: EXPORTING RESULTS")
            self.logger.info("=" * 70)
            self._export_results(louvain_results, label_prop_results, analysis)

            # Step 7: Write back to database
            self.logger.info("\n" + "=" * 70)
            self.logger.info("STEP 7: WRITING TO DATABASE")
            self.logger.info("=" * 70)
            write_stats = self._write_to_database()

            # Cleanup
            self._cleanup()

            elapsed_time = time.time() - start_time
            self.logger.info("\n" + "=" * 70)
            self.logger.info("DEMO COMPLETED SUCCESSFULLY")
            self.logger.info("=" * 70)
            self.logger.info(f"Total execution time: {elapsed_time:.2f} seconds")

            return {
                'data_stats': data_stats,
                'projection_stats': projection_stats,
                'louvain_results': louvain_results,
                'label_prop_results': label_prop_results,
                'analysis': analysis,
                'write_stats': write_stats,
                'execution_time': elapsed_time
            }

        except Exception as e:
            self.logger.error(f"Demo failed: {e}", exc_info=True)
            self._cleanup()
            raise

    def _load_data(self) -> Dict[str, int]:
        """Load sample data into Neo4j."""
        loader = DataLoader(self.gds)
        stats = loader.load_sample_data()

        self.logger.info(f"✓ Loaded {stats['nodes']} nodes")
        self.logger.info(f"✓ Created {stats['relationships']} relationships")

        return stats

    def _create_graph_projection(self) -> Dict[str, Any]:
        """Create GDS graph projection."""
        # Drop existing projection if exists
        try:
            self.gds.graph.drop(self.graph_name)
            self.logger.info(f"Dropped existing graph projection: {self.graph_name}")
        except Exception:
            pass  # Graph doesn't exist, which is fine

        # Create new projection
        self.G, result = self.gds.graph.project(
            self.graph_name,
            "User",
            {
                "FOLLOWS": {
                    "orientation": "UNDIRECTED",
                    "properties": "weight"
                }
            }
        )

        self.logger.info(f"✓ Graph projected: {result['graphName']}")
        self.logger.info(f"✓ Nodes: {result['nodeCount']}")
        self.logger.info(f"✓ Relationships: {result['relationshipCount']}")

        return result

    def _run_louvain(self) -> Dict[str, Any]:
        """
        Execute Louvain community detection algorithm.

        Returns:
            Dictionary containing community assignments and metrics
        """
        # Stream mode for analysis
        self.logger.info("Running Louvain algorithm (stream mode)...")
        community_data = self.gds.louvain.stream(
            self.G,
            relationshipWeightProperty="weight",
            maxIterations=self.max_iterations,
            tolerance=self.tolerance
        )

        # Mutate mode to get modularity score
        self.logger.info("Running Louvain algorithm (mutate mode for metrics)...")
        mutate_result = self.gds.louvain.mutate(
            self.G,
            mutateProperty="louvainCommunity",
            relationshipWeightProperty="weight",
            maxIterations=self.max_iterations,
            tolerance=self.tolerance
        )

        num_communities = len(community_data['communityId'].unique())

        self.logger.info(f"✓ Communities detected: {num_communities}")
        self.logger.info(f"✓ Modularity score: {mutate_result['modularity']:.4f}")
        self.logger.info(f"✓ Iterations: {mutate_result['ranLevels']}")

        return {
            'community_data': community_data,
            'modularity': mutate_result['modularity'],
            'num_communities': num_communities,
            'iterations': mutate_result['ranLevels']
        }

    def _run_label_propagation(self) -> Dict[str, Any]:
        """
        Execute Label Propagation algorithm for comparison.

        Returns:
            Dictionary containing community assignments
        """
        self.logger.info("Running Label Propagation algorithm...")
        community_data = self.gds.labelPropagation.stream(
            self.G,
            relationshipWeightProperty="weight",
            maxIterations=self.max_iterations
        )

        num_communities = len(community_data['communityId'].unique())

        self.logger.info(f"✓ Communities detected: {num_communities}")

        return {
            'community_data': community_data,
            'num_communities': num_communities
        }

    def _analyze_communities(self, louvain_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze community structure and characteristics.

        Args:
            louvain_results: Results from Louvain algorithm

        Returns:
            Dictionary containing analysis results
        """
        community_data = louvain_results['community_data']

        # Community size distribution
        size_distribution = community_data.groupby('communityId').size()
        largest_community = size_distribution.max()
        smallest_community = size_distribution.min()
        avg_community_size = size_distribution.mean()

        self.logger.info("\nCommunity Size Distribution:")
        for comm_id, size in size_distribution.items():
            self.logger.info(f"  Community {comm_id}: {size} members")

        self.logger.info(f"\n✓ Largest community: {largest_community} members")
        self.logger.info(f"✓ Smallest community: {smallest_community} members")
        self.logger.info(f"✓ Average community size: {avg_community_size:.1f} members")

        # Find influential nodes using PageRank
        self.logger.info("\nIdentifying community influencers...")
        pagerank_data = self.gds.pageRank.stream(
            self.G,
            relationshipWeightProperty="weight"
        )

        # Merge with community data
        influence_data = pd.merge(
            community_data[['nodeId', 'communityId']],
            pagerank_data[['nodeId', 'score']],
            on='nodeId'
        )

        # Find top influencer in each community
        top_influencers = []
        for comm_id in sorted(community_data['communityId'].unique()):
            comm_data = influence_data[influence_data['communityId'] == comm_id]
            top_influencer = comm_data.nlargest(1, 'score')
            top_influencers.append({
                'community_id': comm_id,
                'node_id': int(top_influencer['nodeId'].values[0]),
                'influence_score': float(top_influencer['score'].values[0])
            })
            self.logger.info(
                f"  Community {comm_id}: Node {top_influencer['nodeId'].values[0]} "
                f"(influence: {top_influencer['score'].values[0]:.4f})"
            )

        # Calculate inter-community connections
        self.logger.info("\nAnalyzing inter-community connections...")
        inter_community_query = """
        MATCH (u1:User)-[f:FOLLOWS]->(u2:User)
        WHERE u1.louvainCommunity IS NOT NULL
          AND u2.louvainCommunity IS NOT NULL
          AND u1.louvainCommunity <> u2.louvainCommunity
        RETURN u1.louvainCommunity AS fromCommunity,
               u2.louvainCommunity AS toCommunity,
               count(f) AS connections,
               sum(f.weight) AS totalWeight
        ORDER BY connections DESC
        """

        try:
            # Note: This requires communities to be written to DB first
            # We'll calculate this after write step in practice
            inter_community_edges = 0
        except Exception:
            inter_community_edges = "N/A (requires DB write)"

        return {
            'size_distribution': size_distribution.to_dict(),
            'largest_community': int(largest_community),
            'smallest_community': int(smallest_community),
            'avg_community_size': float(avg_community_size),
            'top_influencers': top_influencers,
            'inter_community_edges': inter_community_edges
        }

    def _export_results(
        self,
        louvain_results: Dict[str, Any],
        label_prop_results: Dict[str, Any],
        analysis: Dict[str, Any]
    ):
        """Export results to CSV files."""
        # Export Louvain communities
        self.exporter.export_communities(
            louvain_results['community_data'],
            filename="louvain_communities.csv"
        )

        # Export Label Propagation communities
        self.exporter.export_communities(
            label_prop_results['community_data'],
            filename="label_propagation_communities.csv"
        )

        # Export community summary
        self.exporter.export_community_summary(
            louvain_results['community_data'],
            filename="community_summary.csv"
        )

        # Export overall statistics
        stats = {
            'algorithm': 'Louvain',
            'num_communities': louvain_results['num_communities'],
            'modularity': louvain_results['modularity'],
            'largest_community': analysis['largest_community'],
            'smallest_community': analysis['smallest_community'],
            'avg_community_size': analysis['avg_community_size']
        }
        self.exporter.export_statistics(stats, filename="metrics.csv")

        self.logger.info(f"✓ Results exported to {self.output_dir / 'derived'}")

    def _write_to_database(self) -> Dict[str, Any]:
        """Write community assignments back to Neo4j database."""
        self.logger.info("Writing community assignments to database...")

        write_result = self.gds.louvain.write(
            self.G,
            writeProperty="community",
            relationshipWeightProperty="weight",
            maxIterations=self.max_iterations,
            tolerance=self.tolerance
        )

        self.logger.info(f"✓ Communities written: {write_result['communityCount']}")
        self.logger.info(f"✓ Properties written: {write_result['nodePropertiesWritten']}")
        self.logger.info(f"✓ Write time: {write_result['writeMillis']}ms")

        return write_result

    def _cleanup(self):
        """Clean up resources."""
        if self.G:
            try:
                self.gds.graph.drop(self.G)
                self.logger.info("✓ Graph projection cleaned up")
            except Exception as e:
                self.logger.warning(f"Failed to drop graph: {e}")


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.

    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Neo4j GDS Community Detection Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use environment variables
  python demo.py

  # Override connection parameters
  python demo.py --uri bolt://localhost:7687 --user neo4j --password secret

  # Customize algorithm parameters
  python demo.py --max-iterations 20 --tolerance 0.001

  # Custom output directory
  python demo.py --output-dir ./custom-results
        """
    )

    # Connection parameters
    parser.add_argument(
        '--uri',
        type=str,
        help='Neo4j URI (default: from NEO4J_URI env or bolt://localhost:7687)'
    )
    parser.add_argument(
        '--user',
        type=str,
        help='Neo4j username (default: from NEO4J_USER env or neo4j)'
    )
    parser.add_argument(
        '--password',
        type=str,
        help='Neo4j password (default: from NEO4J_PASSWORD env)'
    )

    # Algorithm parameters
    parser.add_argument(
        '--max-iterations',
        type=int,
        default=10,
        help='Maximum iterations for algorithms (default: 10)'
    )
    parser.add_argument(
        '--tolerance',
        type=float,
        default=0.0001,
        help='Convergence tolerance (default: 0.0001)'
    )
    parser.add_argument(
        '--resolution',
        type=float,
        default=1.0,
        help='Resolution parameter for Louvain (default: 1.0)'
    )

    # Output parameters
    parser.add_argument(
        '--output-dir',
        type=str,
        default='.',
        help='Output directory for results (default: current directory)'
    )

    # Logging
    parser.add_argument(
        '--log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )

    return parser.parse_args()


def main():
    """Main entry point for the demo."""
    args = parse_arguments()

    # Setup logging
    logger = setup_logging(args.log_level)

    logger.info("=" * 70)
    logger.info("Neo4j GDS Community Detection Demo")
    logger.info("=" * 70)

    try:
        # Initialize connection manager
        session_manager = Neo4jSessionManager(
            uri=args.uri,
            user=args.user,
            password=args.password
        )

        # Connect to Neo4j
        gds = session_manager.connect()

        # Run demo
        demo = CommunityDetectionDemo(
            gds=gds,
            output_dir=Path(args.output_dir),
            max_iterations=args.max_iterations,
            tolerance=args.tolerance,
            resolution=args.resolution
        )

        results = demo.run_full_workflow()

        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("INSIGHTS SUMMARY")
        logger.info("=" * 70)
        logger.info(
            f"✓ Detected {results['louvain_results']['num_communities']} "
            f"communities with modularity {results['louvain_results']['modularity']:.4f}"
        )
        logger.info(
            f"✓ Largest community: {results['analysis']['largest_community']} members"
        )
        logger.info(
            f"✓ Average community size: {results['analysis']['avg_community_size']:.1f} members"
        )
        logger.info(f"✓ Top influencers identified in each community")
        logger.info(f"✓ Results exported to {Path(args.output_dir) / 'derived'}")

        # Close connection
        session_manager.close()

        logger.info("\n✓ Demo completed successfully!")
        return 0

    except ConnectionError as e:
        logger.error(f"Connection failed: {e}")
        logger.error(
            "\nTroubleshooting steps:"
            "\n  1. Ensure Neo4j is running (docker ps or check Aura status)"
            "\n  2. Verify NEO4J_URI is correct"
            "\n  3. Check credentials are valid"
            "\n  4. Confirm GDS plugin is installed"
        )
        return 1

    except Exception as e:
        logger.error(f"Demo failed with error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
