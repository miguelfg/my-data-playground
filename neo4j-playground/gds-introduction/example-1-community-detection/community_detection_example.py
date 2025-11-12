"""
Neo4j GDS Community Detection - Complete Example
=================================================

Use Case: Social Network Analysis - Finding communities of users
Dataset: Users connected by FOLLOWS relationships with interaction weights

This example demonstrates:
1. Creating sample graph data
2. Graph projection
3. Three community detection algorithms:
   - Louvain (hierarchical, modularity-based)
   - Label Propagation (fast, semi-supervised)
   - Weakly Connected Components (WCC)
4. Comparing results
5. Writing back to database
"""

from graphdatascience import GraphDataScience
import pandas as pd

# ============================================================================
# PART 1: SETUP AND DATA CREATION
# ============================================================================

# Connect to Neo4j
gds = GraphDataScience("bolt://localhost:7687", auth=("neo4j", "test1234"))

# Verify GDS version
print(f"GDS Version: {gds.version()}")

# Create sample social network data - Split into separate statements
# Clear existing data
clear_data_cypher = """
MATCH (n:User) DETACH DELETE n
"""

create_data_cypher = """
// Create users
CREATE (alice:User {name: 'Alice', userId: 1})
CREATE (bob:User {name: 'Bob', userId: 2})
CREATE (carol:User {name: 'Carol', userId: 3})
CREATE (david:User {name: 'David', userId: 4})
CREATE (eve:User {name: 'Eve', userId: 5})
CREATE (frank:User {name: 'Frank', userId: 6})
CREATE (grace:User {name: 'Grace', userId: 7})
CREATE (henry:User {name: 'Henry', userId: 8})
CREATE (iris:User {name: 'Iris', userId: 9})
CREATE (jack:User {name: 'Jack', userId: 10})

// Create FOLLOWS relationships with weights (interaction strength)
// Community 1: Alice, Bob, Carol (tight-knit group)
CREATE (alice)-[:FOLLOWS {weight: 10}]->(bob)
CREATE (bob)-[:FOLLOWS {weight: 8}]->(alice)
CREATE (alice)-[:FOLLOWS {weight: 9}]->(carol)
CREATE (carol)-[:FOLLOWS {weight: 7}]->(alice)
CREATE (bob)-[:FOLLOWS {weight: 12}]->(carol)
CREATE (carol)-[:FOLLOWS {weight: 11}]->(bob)

// Community 2: David, Eve, Frank (another tight-knit group)
CREATE (david)-[:FOLLOWS {weight: 9}]->(eve)
CREATE (eve)-[:FOLLOWS {weight: 8}]->(david)
CREATE (david)-[:FOLLOWS {weight: 10}]->(frank)
CREATE (frank)-[:FOLLOWS {weight: 9}]->(david)
CREATE (eve)-[:FOLLOWS {weight: 11}]->(frank)
CREATE (frank)-[:FOLLOWS {weight: 10}]->(eve)

// Community 3: Grace, Henry, Iris (loose group)
CREATE (grace)-[:FOLLOWS {weight: 5}]->(henry)
CREATE (henry)-[:FOLLOWS {weight: 4}]->(iris)
CREATE (iris)-[:FOLLOWS {weight: 3}]->(grace)

// Bridge connections (weak ties between communities)
CREATE (carol)-[:FOLLOWS {weight: 2}]->(david)
CREATE (frank)-[:FOLLOWS {weight: 1}]->(grace)
CREATE (jack)-[:FOLLOWS {weight: 1}]->(alice)
CREATE (jack)-[:FOLLOWS {weight: 1}]->(grace)

RETURN count(*) as relationships_created
"""

# Execute data creation
gds.run_cypher(clear_data_cypher)
gds.run_cypher(create_data_cypher)
print("Sample data created successfully")

# ============================================================================
# PART 2: GRAPH PROJECTION
# ============================================================================

print("\n" + "="*70)
print("PROJECTING GRAPH")
print("="*70)

# Method 1: Using Python GDS Client
G, result = gds.graph.project(
    "social-network",                    # Graph name
    "User",                              # Node projection
    {                                    # Relationship projection
        "FOLLOWS": {
            "orientation": "UNDIRECTED",  # Treat as undirected for community detection
            "properties": "weight"        # Include weight property
        }
    }
)

print(f"Graph projected: {result['graphName']}")
print(f"Nodes: {result['nodeCount']}")
print(f"Relationships: {result['relationshipCount']}")

# Method 2: Alternative Cypher approach
cypher_projection = """
CALL gds.graph.project(
    'social-network-cypher',
    'User',
    {
        FOLLOWS: {
            orientation: 'UNDIRECTED',
            properties: 'weight'
        }
    }
)
YIELD graphName, nodeCount, relationshipCount
"""

# ============================================================================
# PART 3: LOUVAIN ALGORITHM
# ============================================================================

print("\n" + "="*70)
print("ALGORITHM 1: LOUVAIN (Hierarchical Community Detection)")
print("="*70)

# Python API - Stream mode (for analysis)
louvain_result = gds.louvain.stream(
    G,
    relationshipWeightProperty="weight",
    maxIterations=10,
    tolerance=0.0001
)

print("\nLouvain Communities:")
print(louvain_result.sort_values('communityId'))

# Get community statistics
print("\nCommunity Statistics:")
print(louvain_result.groupby('communityId').size().to_frame('members'))

# Python API - Mutate mode (store in projected graph)
mutate_result = gds.louvain.mutate(
    G,
    mutateProperty="louvainCommunity",
    relationshipWeightProperty="weight"
)

print(f"\nModularity Score: {mutate_result['modularity']:.4f}")
print(f"Communities Found: {mutate_result['communityCount']}")

# Cypher equivalent
louvain_cypher = """
// Stream mode
CALL gds.louvain.stream('social-network', {
    relationshipWeightProperty: 'weight',
    maxIterations: 10,
    tolerance: 0.0001
})
YIELD nodeId, communityId, intermediateCommunityIds
RETURN gds.util.asNode(nodeId).name AS name, 
       communityId,
       intermediateCommunityIds
ORDER BY communityId, name;

// Stats mode (for evaluation)
CALL gds.louvain.stats('social-network', {
    relationshipWeightProperty: 'weight'
})
YIELD communityCount, modularity, modularities;

// Write mode (persist to database)
CALL gds.louvain.write('social-network', {
    writeProperty: 'louvainCommunity',
    relationshipWeightProperty: 'weight'
})
YIELD communityCount, modularity, writeMillis;
"""

# ============================================================================
# PART 4: LABEL PROPAGATION ALGORITHM
# ============================================================================

print("\n" + "="*70)
print("ALGORITHM 2: LABEL PROPAGATION (Fast Community Detection)")
print("="*70)

# Python API
label_prop_result = gds.labelPropagation.stream(
    G,
    relationshipWeightProperty="weight",
    maxIterations=10
)

print("\nLabel Propagation Communities:")
print(label_prop_result.sort_values('communityId'))

# Compare with Louvain
comparison = pd.merge(
    louvain_result[['nodeId', 'communityId']].rename(columns={'communityId': 'louvain'}),
    label_prop_result[['nodeId', 'communityId']].rename(columns={'communityId': 'labelProp'}),
    on='nodeId'
)
print("\nAlgorithm Comparison:")
print(comparison)

# Cypher equivalent
label_prop_cypher = """
// Stream mode
CALL gds.labelPropagation.stream('social-network', {
    relationshipWeightProperty: 'weight',
    maxIterations: 10
})
YIELD nodeId, communityId
RETURN gds.util.asNode(nodeId).name AS name, 
       communityId
ORDER BY communityId, name;

// Mutate mode (for further analysis)
CALL gds.labelPropagation.mutate('social-network', {
    mutateProperty: 'labelPropCommunity',
    relationshipWeightProperty: 'weight'
})
YIELD communityCount, ranIterations;
"""

# ============================================================================
# PART 5: WEAKLY CONNECTED COMPONENTS (WCC)
# ============================================================================

print("\n" + "="*70)
print("ALGORITHM 3: WEAKLY CONNECTED COMPONENTS")
print("="*70)

# Python API
wcc_result = gds.wcc.stream(G)

print("\nConnected Components:")
print(wcc_result.sort_values('componentId'))

print("\nComponent Sizes:")
print(wcc_result.groupby('componentId').size().to_frame('size'))

# Cypher equivalent
wcc_cypher = """
// Stream mode
CALL gds.wcc.stream('social-network')
YIELD nodeId, componentId
RETURN gds.util.asNode(nodeId).name AS name, 
       componentId
ORDER BY componentId, name;

// Stats mode
CALL gds.wcc.stats('social-network')
YIELD componentCount, componentDistribution;
"""

# ============================================================================
# PART 6: COMMUNITY ANALYSIS
# ============================================================================

print("\n" + "="*70)
print("COMMUNITY ANALYSIS")
print("="*70)

# Find most influential users in each community (using PageRank)
pagerank_result = gds.pageRank.stream(
    G,
    relationshipWeightProperty="weight"
)

# Merge with community data
community_influence = pd.merge(
    louvain_result[['nodeId', 'communityId']],
    pagerank_result[['nodeId', 'score']],
    on='nodeId'
)

print("\nTop Influencers by Community:")
for comm_id in sorted(community_influence['communityId'].unique()):
    top_user = community_influence[
        community_influence['communityId'] == comm_id
    ].nlargest(1, 'score')
    print(f"Community {comm_id}: Node {top_user['nodeId'].values[0]} "
          f"(PageRank: {top_user['score'].values[0]:.4f})")

# ============================================================================
# PART 7: WRITE RESULTS BACK TO DATABASE
# ============================================================================

print("\n" + "="*70)
print("WRITING RESULTS TO DATABASE")
print("="*70)

# Write Louvain communities
write_result = gds.louvain.write(
    G,
    writeProperty="community",
    relationshipWeightProperty="weight"
)

print(f"Communities written: {write_result['communityCount']}")
print(f"Properties written: {write_result['nodePropertiesWritten']}")

# Cypher to query results
query_results = """
MATCH (u:User)
RETURN u.name AS name, 
       u.community AS community
ORDER BY u.community, u.name;
"""

# ============================================================================
# PART 8: ADVANCED - COMMUNITY QUALITY METRICS
# ============================================================================

print("\n" + "="*70)
print("COMMUNITY QUALITY METRICS")
print("="*70)

# Calculate modularity (already from Louvain)
print(f"Louvain Modularity: {mutate_result['modularity']:.4f}")

# Calculate clustering coefficient for each community
triangle_result = gds.triangleCount.stream(G)
clustering_result = gds.localClusteringCoefficient.stream(G)

# Merge and analyze
quality_metrics = pd.merge(
    louvain_result[['nodeId', 'communityId']],
    clustering_result[['nodeId', 'localClusteringCoefficient']],
    on='nodeId'
)

print("\nAverage Clustering Coefficient by Community:")
print(quality_metrics.groupby('communityId')['localClusteringCoefficient'].mean())

# ============================================================================
# PART 9: CLEANUP
# ============================================================================

print("\n" + "="*70)
print("CLEANUP")
print("="*70)

# Drop the projected graph
gds.graph.drop(G)
print("Graph projection dropped")

# ============================================================================
# COMPLETE CYPHER SCRIPT (for reference)
# ============================================================================

complete_cypher_script = """
// ============================================================
// COMPLETE CYPHER WORKFLOW FOR COMMUNITY DETECTION
// ============================================================

// 1. PROJECT GRAPH
CALL gds.graph.project(
    'social-network',
    'User',
    {
        FOLLOWS: {
            orientation: 'UNDIRECTED',
            properties: 'weight'
        }
    }
)
YIELD graphName, nodeCount, relationshipCount;

// 2. MEMORY ESTIMATION (best practice before running)
CALL gds.louvain.stream.estimate('social-network', {
    relationshipWeightProperty: 'weight'
})
YIELD requiredMemory, bytesMin, bytesMax;

// 3. RUN LOUVAIN (stream for analysis)
CALL gds.louvain.stream('social-network', {
    relationshipWeightProperty: 'weight'
})
YIELD nodeId, communityId
WITH gds.util.asNode(nodeId) AS user, communityId
RETURN user.name AS name, communityId
ORDER BY communityId, name;

// 4. RUN LOUVAIN (write to persist)
CALL gds.louvain.write('social-network', {
    writeProperty: 'community',
    relationshipWeightProperty: 'weight'
})
YIELD communityCount, modularity, modularities, writeMillis;

// 5. ANALYZE COMMUNITIES
MATCH (u:User)
WITH u.community AS communityId, collect(u.name) AS members
RETURN communityId, size(members) AS size, members
ORDER BY size DESC;

// 6. FIND INTER-COMMUNITY CONNECTIONS
MATCH (u1:User)-[f:FOLLOWS]->(u2:User)
WHERE u1.community <> u2.community
RETURN u1.community AS fromCommunity, 
       u2.community AS toCommunity,
       count(f) AS connections
ORDER BY connections DESC;

// 7. FIND COMMUNITY LEADERS (highest PageRank within community)
CALL gds.pageRank.stream('social-network', {
    relationshipWeightProperty: 'weight'
})
YIELD nodeId, score
WITH gds.util.asNode(nodeId) AS user, score
ORDER BY user.community, score DESC
WITH user.community AS communityId, 
     collect({name: user.name, score: score})[0] AS leader
RETURN communityId, leader.name AS leaderName, leader.score AS influence;

// 8. CLEANUP
CALL gds.graph.drop('social-network')
YIELD graphName;
"""

print("\n" + "="*70)
print("EXAMPLE COMPLETE!")
print("="*70)
print("\nKey Takeaways:")
print("1. Louvain: Best for hierarchical communities, optimizes modularity")
print("2. Label Propagation: Fastest, good for large graphs")
print("3. WCC: Finds disconnected components")
print("4. Always compare results from multiple algorithms")
print("5. Use weights when available for better accuracy")
