# Example 1: Community Detection with Neo4j GDS

This example demonstrates end-to-end community detection using Neo4j Graph Data Science (GDS) library. It showcases how to identify communities in a social network using multiple algorithms and interpret the results.

## 📋 Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Dataset](#dataset)
- [Algorithms](#algorithms)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Output](#output)
- [Example Results](#example-results)
- [Troubleshooting](#troubleshooting)
- [Further Reading](#further-reading)

## Overview

**Use Case**: Social Network Analysis - Finding communities of users

This demo shows how to:
1. Connect to Neo4j using secure credential management
2. Load a sample social network dataset
3. Create a graph projection in GDS
4. Run multiple community detection algorithms:
   - **Louvain**: Hierarchical, modularity-based community detection
   - **Label Propagation**: Fast, semi-supervised approach
5. Analyze and compare results
6. Export findings to CSV for further analysis
7. Write results back to the database

## Quick Start

```bash
# 1. Start Neo4j with GDS plugin
cd /path/to/gds-introduction
make docker-neo4j-run

# 2. Configure environment (first time only)
cp template.env .env
# Edit .env and set your password

# 3. Install dependencies
make install

# 4. Run the demo
make run-example-1

# Or run directly with Python
uv run python example-1-community-detection/demo.py
```

**Expected Runtime**: < 60 seconds

## Dataset

The demo uses a synthetic social network with **10 users** divided into **3 distinct communities**:

### Community Structure

**Community 1: Alice, Bob, Carol** (tight-knit group)
- Strong connections with high interaction weights (7-12)
- High reciprocity and dense internal connections

**Community 2: David, Eve, Frank** (another tight-knit group)
- Strong connections with high interaction weights (8-11)
- Similar structure to Community 1

**Community 3: Grace, Henry, Iris** (loose group)
- Weaker connections with lower weights (3-5)
- Less dense structure

**Bridge Connections**:
- Jack acts as a peripheral node connecting to multiple communities
- Weak ties between communities (weight 1-2) representing cross-community interactions

### Graph Statistics
- **Nodes**: 10 users
- **Relationships**: 20 directed FOLLOWS edges (treated as undirected for analysis)
- **Properties**: Each relationship has a `weight` property representing interaction strength

## Algorithms

### 1. Louvain Community Detection

**Purpose**: Hierarchical community detection optimizing modularity

**How it works**:
1. Initially, each node is its own community
2. Iteratively moves nodes to maximize modularity gain
3. Creates hierarchical levels of communities

**Parameters**:
- `maxIterations`: Maximum optimization iterations (default: 10)
- `tolerance`: Convergence threshold (default: 0.0001)
- `relationshipWeightProperty`: Uses edge weights for better accuracy

**Output**: Community assignments + modularity score (0-1, higher is better)

### 2. Label Propagation

**Purpose**: Fast community detection using label spreading

**How it works**:
1. Each node starts with unique label
2. Iteratively updates labels based on neighbor majority
3. Converges when labels stabilize

**Parameters**:
- `maxIterations`: Maximum propagation rounds (default: 10)
- `relationshipWeightProperty`: Weighted neighbor influence

**Output**: Community assignments

### Algorithm Comparison

| Algorithm | Speed | Accuracy | Hierarchy | Best For |
|-----------|-------|----------|-----------|----------|
| Louvain | Medium | High | Yes | General-purpose, quality matters |
| Label Propagation | Fast | Medium | No | Large graphs, speed priority |

## Prerequisites

### Neo4j Setup

**Option 1: Docker (Recommended)**
```bash
# Already configured in Makefile
make docker-neo4j-run

# Verify Neo4j is running
docker ps | grep neo4j-gds-intro

# Access Neo4j Browser: http://localhost:7474
```

**Option 2: Neo4j Aura (Cloud)**
1. Create free instance at [neo4j.com/aura](https://neo4j.com/aura)
2. Install GDS plugin from Aura console
3. Update `.env` with your Aura connection URI

**Option 3: Local Neo4j Desktop**
1. Install from [neo4j.com/download](https://neo4j.com/download)
2. Create database with GDS plugin enabled
3. Update `.env` with `bolt://localhost:7687`

### Verify GDS Installation

```cypher
// Run in Neo4j Browser
RETURN gds.version() AS gdsVersion
```

Expected: GDS version 2.x or higher

### Python Requirements

- Python 3.13+
- `uv` package manager (or `pip`)
- Dependencies listed in `pyproject.toml`

## Installation

### 1. Environment Setup

```bash
# Clone/navigate to project root
cd /path/to/my-data-playground/neo4j-playground/gds-introduction

# Create .env file from template
cp template.env .env

# Edit .env with your credentials
# For Docker default:
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=test1234  # Change this!
```

**Security Note**: Never commit `.env` to version control. It's already in `.gitignore`.

### 2. Install Dependencies

```bash
# Using uv (recommended)
make install

# Or using pip
pip install -r requirements.txt  # if you have requirements.txt
# Or install from pyproject.toml
pip install .
```

### 3. Start Neo4j

```bash
# Start Docker container
make docker-neo4j-run

# Wait ~30 seconds for Neo4j to initialize
# Check logs: docker logs neo4j-gds-intro

# Verify connection
curl http://localhost:7474  # Should return Neo4j page
```

## Usage

### Basic Usage

```bash
# Run with environment variables from .env
make run-example-1

# Or directly
uv run python example-1-community-detection/demo.py
```

### Advanced Usage with CLI Parameters

```bash
# Override connection settings
python demo.py \
  --uri bolt://localhost:7687 \
  --user neo4j \
  --password mypassword

# Customize algorithm parameters
python demo.py \
  --max-iterations 20 \
  --tolerance 0.001

# Custom output directory
python demo.py --output-dir ./my-results

# Debug mode with verbose logging
python demo.py --log-level DEBUG

# Combine multiple options
python demo.py \
  --uri bolt://aura-uri.neo4j.io:7687 \
  --user neo4j \
  --password aura-password \
  --max-iterations 15 \
  --output-dir ./aura-results \
  --log-level INFO
```

### Configuration Options

| Parameter | Environment Variable | CLI Flag | Default | Description |
|-----------|---------------------|----------|---------|-------------|
| URI | `NEO4J_URI` | `--uri` | `bolt://localhost:7687` | Neo4j connection URI |
| Username | `NEO4J_USER` | `--user` | `neo4j` | Database username |
| Password | `NEO4J_PASSWORD` | `--password` | (required) | Database password |
| Max Iterations | - | `--max-iterations` | 10 | Algorithm iterations |
| Tolerance | - | `--tolerance` | 0.0001 | Convergence threshold |
| Resolution | - | `--resolution` | 1.0 | Louvain resolution |
| Output Dir | - | `--output-dir` | `.` | CSV output directory |
| Log Level | - | `--log-level` | INFO | Logging verbosity |

## Output

### Console Output

The demo provides structured logging showing:
1. ✅ Connection establishment
2. ✅ Data loading progress
3. ✅ Graph projection statistics
4. ✅ Algorithm execution metrics
5. ✅ Community analysis insights
6. ✅ Export confirmation

### CSV Exports

All results are saved to `<output-dir>/derived/`:

**1. `louvain_communities.csv`**
```csv
nodeId,communityId
0,1
1,1
2,1
3,2
...
```

**2. `label_propagation_communities.csv`**
```csv
nodeId,communityId
0,5
1,5
...
```

**3. `community_summary.csv`**
```csv
communityId,member_count
1,3
2,3
3,3
4,1
```

**4. `metrics.csv`**
```csv
algorithm,num_communities,modularity,largest_community,smallest_community,avg_community_size
Louvain,4,0.4025,3,1,2.5
```

### Database Properties

After execution, each `User` node has a `community` property:

```cypher
MATCH (u:User)
RETURN u.name AS name, u.community AS community
ORDER BY u.community, u.name;
```

## Example Results

### Expected Output

```
======================================================================
Neo4j GDS Community Detection Demo
======================================================================
2025-01-12 10:30:15 - INFO - Connecting to Neo4j at bolt://localhost:7687
2025-01-12 10:30:15 - INFO - Successfully connected. GDS Version: 2.7.0

======================================================================
STEP 1: DATA LOADING
======================================================================
2025-01-12 10:30:16 - INFO - Clearing existing data
2025-01-12 10:30:16 - INFO - Data loaded successfully: 10 nodes, 20 relationships
✓ Loaded 10 nodes
✓ Created 20 relationships

======================================================================
STEP 2: GRAPH PROJECTION
======================================================================
✓ Graph projected: social-network-demo
✓ Nodes: 10
✓ Relationships: 20

======================================================================
STEP 3: LOUVAIN COMMUNITY DETECTION
======================================================================
✓ Communities detected: 4
✓ Modularity score: 0.4025
✓ Iterations: 2

======================================================================
STEP 5: COMMUNITY ANALYSIS
======================================================================

Community Size Distribution:
  Community 0: 3 members
  Community 1: 3 members
  Community 2: 3 members
  Community 10: 1 members

✓ Largest community: 3 members
✓ Smallest community: 1 members
✓ Average community size: 2.5 members

Identifying community influencers...
  Community 0: Node 2 (influence: 0.1542)
  Community 1: Node 4 (influence: 0.1542)
  Community 2: Node 7 (influence: 0.1125)
  Community 10: Node 9 (influence: 0.0375)

======================================================================
INSIGHTS SUMMARY
======================================================================
✓ Detected 4 communities with modularity 0.4025
✓ Largest community: 3 members
✓ Average community size: 2.5 members
✓ Top influencers identified in each community
✓ Results exported to ./derived

✓ Demo completed successfully!
```

### Interpretation

**Key Findings**:
1. **4 communities detected** - The algorithm identified the expected 3 main communities plus Jack as a separate peripheral node
2. **Modularity score: 0.4025** - Moderate modularity indicates clear community structure but with some overlap
3. **Community sizes: 3, 3, 3, 1** - Expected distribution matching the designed structure
4. **Top influencers** - PageRank identifies central nodes within each community

**Business Insights**:
- **Tight-knit groups**: Communities 0, 1, 2 show strong internal cohesion
- **Bridge nodes**: Jack (community 10) connects multiple communities - potential influencer for cross-community initiatives
- **Weak ties**: Carol-David and Frank-Grace connections are inter-community bridges that prevent complete separation

## Troubleshooting

### Connection Errors

**Problem**: `ConnectionError: Unable to connect to Neo4j`

**Solutions**:
```bash
# 1. Check if Neo4j is running
docker ps | grep neo4j-gds-intro

# 2. Start Neo4j if not running
make docker-neo4j-start

# 3. Check Neo4j logs
docker logs neo4j-gds-intro

# 4. Verify credentials in .env
cat .env | grep NEO4J

# 5. Test connection manually
curl http://localhost:7474
```

### GDS Plugin Missing

**Problem**: `Graph Data Science library not available`

**Solutions**:
```bash
# For Docker: Already included in neo4j:latest with GDS plugin
# Just restart the container
make docker-neo4j-remove
make docker-neo4j-run

# For Aura: Install GDS plugin from Aura console

# For Desktop: Enable GDS plugin in database settings
```

### Password Authentication Failed

**Problem**: `AuthError: The client is unauthorized`

**Solutions**:
1. Check `.env` file has correct password
2. For Docker default, use `neo4j/test1234`
3. Reset password:
```bash
docker exec -it neo4j-gds-intro cypher-shell -u neo4j -p oldpassword
# Then: ALTER USER neo4j SET PASSWORD 'newpassword'
```

### Permission Denied on Output Directory

**Problem**: `PermissionError: [Errno 13] Permission denied: './derived'`

**Solutions**:
```bash
# Create directory with proper permissions
mkdir -p ./data/derived
chmod 755 ./data/derived

# Or use different output directory
python demo.py --output-dir ~/my-results
```

### Dependency Issues

**Problem**: `ModuleNotFoundError: No module named 'graphdatascience'`

**Solutions**:
```bash
# Reinstall dependencies
uv sync

# Or with pip
pip install graphdatascience pandas

# Verify installation
python -c "import graphdatascience; print(graphdatascience.__version__)"
```

## Further Reading

### Neo4j GDS Documentation
- [GDS Manual](https://neo4j.com/docs/graph-data-science/current/)
- [Louvain Algorithm](https://neo4j.com/docs/graph-data-science/current/algorithms/louvain/)
- [Label Propagation](https://neo4j.com/docs/graph-data-science/current/algorithms/label-propagation/)
- [Python Client](https://neo4j.com/docs/graph-data-science-client/current/)

### Community Detection Theory
- [Modularity and Community Structure](https://www.pnas.org/doi/10.1073/pnas.0601602103)
- [Fast Unfolding of Communities (Louvain)](https://arxiv.org/abs/0803.0476)
- [Label Propagation Algorithm](https://journals.aps.org/pre/abstract/10.1103/PhysRevE.76.036106)

### Graph Data Science Applications
- [Social Network Analysis](https://neo4j.com/use-cases/social-network/)
- [Fraud Detection with GDS](https://neo4j.com/use-cases/fraud-detection/)
- [Recommendation Engines](https://neo4j.com/use-cases/real-time-recommendation-engine/)

---

## Next Steps

After completing this example, explore:
1. **Example 2**: Centrality algorithms (PageRank, Betweenness, Degree)
2. **Example 3**: Link prediction and similarity algorithms
3. **Example 4**: Path finding and network flow
4. **Custom Datasets**: Apply these algorithms to your own data

## Support

For issues or questions:
- [Neo4j Community Forum](https://community.neo4j.com/)
- [GitHub Issues](https://github.com/neo4j/graph-data-science)
- [Neo4j Discord](https://discord.gg/neo4j)
