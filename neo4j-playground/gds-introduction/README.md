# Neo4j Graph Data Science (GDS) Introduction

This directory contains examples, notebooks, and scripts that introduce the Graph Data Science (GDS) library. These resources cover basic concepts, algorithms, and practical applications of GDS in Neo4j.

## 🚀 Quick Start

```bash
# 1. Start Neo4j with GDS plugin
make docker-neo4j-run

# 2. Install dependencies
make install

# 3. Run Example 1 - Community Detection
make run-example-1
```

## 📚 Examples

### [Example 1: Community Detection](example-1-community-detection/)

**Status**: ✅ Complete

Demonstrates end-to-end community detection using Louvain and Label Propagation algorithms on a social network.

**What You'll Learn**:
- Graph projection in GDS
- Running community detection algorithms
- Analyzing and comparing results
- Exporting data for further analysis

**Runtime**: < 60 seconds
**Difficulty**: Beginner

[📖 Read the full guide →](example-1-community-detection/README.md)

### Example 2: Centrality Algorithms (Coming Soon)

PageRank, Betweenness, and Degree Centrality for identifying influential nodes.

### Example 3: Similarity & Link Prediction (Coming Soon)

Node similarity algorithms and link prediction for recommendation systems.

## 🐳 Docker Setup

### Start Neo4j with GDS Plugin

```bash
# Start container (includes APOC and GDS plugins)
make docker-neo4j-run

# Verify it's running
docker ps | grep neo4j-gds-intro

# Access Neo4j Browser
open http://localhost:7474
```

### Docker Commands

```bash
make docker-neo4j-start   # Start existing container
make docker-neo4j-stop    # Stop container
make docker-neo4j-remove  # Remove container
```

**Default Credentials**:
- Username: `neo4j`
- Password: `test1234` (configured in `.env`)

## 🔧 Configuration

Create a `.env` file from the template:

```bash
cp template.env .env
# Edit .env with your credentials
```

**Environment Variables**:
- `NEO4J_AUTH`: Docker authentication (format: `username/password`)
- `NEO4J_URI`: Connection URI (default: `bolt://localhost:7687`)
- `NEO4J_USER`: Database username
- `NEO4J_PASSWORD`: Database password

## 📦 Dependencies

Managed with `uv` package manager:

```bash
# Install all dependencies
make install

# Or manually with uv
uv sync
```

**Key Dependencies**:
- `graphdatascience>=1.17`: Official GDS Python client
- `pandas>=2.3`: Data analysis and manipulation
- `jupyter`: Interactive notebooks
- `matplotlib`, `seaborn`: Visualization

## 📖 Resources

### Neo4j GDS Documentation
- [Official GDS Manual](https://neo4j.com/docs/graph-data-science/current/)
- [Python Client Docs](https://neo4j.com/docs/graph-data-science-client/current/)
- [Algorithm Catalog](https://neo4j.com/docs/graph-data-science/current/algorithms/)

### Learning Paths
- [Neo4j GraphAcademy - GDS Course](https://graphacademy.neo4j.com/courses/gds-product-introduction/)
- [Community Forum](https://community.neo4j.com/)
- [Discord Server](https://discord.gg/neo4j)

## 🛠️ Troubleshooting

### Neo4j Won't Start

```bash
# Check if port 7687 is already in use
lsof -i :7687

# Check container logs
docker logs neo4j-gds-intro

# Remove and recreate container
make docker-neo4j-remove
make docker-neo4j-run
```

### Connection Errors

```bash
# Verify Neo4j is running
curl http://localhost:7474

# Check credentials in .env
cat .env | grep NEO4J

# Test connection manually
docker exec -it neo4j-gds-intro cypher-shell -u neo4j -p test1234
```

### GDS Plugin Missing

For Neo4j Desktop or Aura:
1. Go to database settings
2. Add "Graph Data Science" plugin
3. Restart database

## 🤝 Contributing

When adding new examples:
1. Create a new directory: `example-N-descriptive-name/`
2. Include comprehensive README.md
3. Add Makefile target: `run-example-N`
4. Update this main README with example link
5. Test end-to-end workflow

## 📝 License

This project is part of the my-data-playground repository.