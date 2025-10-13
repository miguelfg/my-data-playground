# Databricks SQL - Anki Flashcard Deck

This directory contains Anki flashcards for learning Databricks SQL concepts, commands, and best practices.

## 📚 Card Files

1. **01_basic_cards.txt** - Fundamental concepts and definitions (25 cards)
   - SQL Warehouses
   - Delta Lake basics
   - Core commands (OPTIMIZE, VACUUM, DESCRIBE HISTORY)
   - Time Travel
   - Configuration basics

2. **02_cloze_cards.txt** - Cloze deletion cards for active recall (43 cards)
   - Command syntax with blanks
   - Technical terms and concepts
   - API endpoints
   - Configuration parameters

3. **03_reverse_cards.txt** - Bidirectional learning cards (50 cards)
   - Command ↔ Purpose mapping
   - Term ↔ Definition
   - Parameter ↔ Function

4. **04_code_cards.txt** - Code examples and syntax (48 cards)
   - SQL command examples
   - API usage patterns
   - Configuration examples
   - Practical scenarios

5. **05_concept_cards.txt** - Deep conceptual understanding (40 cards)
   - Architecture decisions
   - Trade-offs and best practices
   - When to use specific features
   - Performance optimization

## 📊 Total Cards: 206

## 🎯 Topics Covered

### Delta Lake
- OPTIMIZE (bin-packing, Z-ordering, liquid clustering)
- VACUUM and retention policies
- Time Travel (VERSION AS OF, TIMESTAMP AS OF, @ syntax)
- Schema evolution (ADD/REPLACE COLUMNS)
- Data migration (CONVERT TO DELTA, CLONE)
- Row tracking and statistics
- Transaction log and ACID properties

### SQL Warehouses
- Creation and configuration
- Lifecycle management (start, stop, delete)
- Sizing and scaling (min/max clusters, cluster sizes)
- Photon and serverless compute
- Auto-stop configuration
- Spot instance policies
- API endpoints and CLI commands

### Performance Optimization
- Data skipping and statistics
- ZORDER BY vs liquid clustering
- Optimized writes
- Partition vs clustering strategies
- ANALYZE TABLE options
- Cache management

### Advanced Features
- Unity Catalog integration
- Row tracking for CDC
- INSERT REPLACE operations
- RESTORE command
- Table features and protocol versions
- Streaming query optimization

## 📥 How to Import into Anki

### Method 1: Text Import (Recommended)
1. Open Anki
2. File → Import
3. Select a card file (e.g., `01_basic_cards.txt`)
4. Configure import settings:
   - **Type**: Basic (for basic_cards, reverse_cards, code_cards, concept_cards)
   - **Type**: Cloze (for cloze_cards)
   - **Deck**: Create new deck called "Databricks SQL"
   - **Field separator**: Pipe (|)
   - **Allow HTML**: Yes
5. Click Import

### Method 2: Import All Files
Repeat the import process for all 5 files into the same deck.

## 🎓 Study Recommendations

### Beginner Path (Weeks 1-2)
1. Start with **01_basic_cards.txt** - Build foundational knowledge
2. Move to **04_code_cards.txt** - Learn syntax through examples
3. Practice with **02_cloze_cards.txt** - Test command recall

### Intermediate Path (Weeks 3-4)
1. Study **03_reverse_cards.txt** - Strengthen bidirectional recall
2. Deep dive into **05_concept_cards.txt** - Understand trade-offs and architecture

### Advanced Practice
- Mix all card types for comprehensive review
- Focus on weak areas identified by Anki's algorithm
- Create your own cards based on real-world scenarios

## 🔧 Anki Settings Recommendations

```
New cards per day: 20-30
Reviews per day: 200
Graduating interval: 3 days
Easy interval: 4 days
Starting ease: 250%
```

## 📖 Study Tips

1. **Context matters**: Don't just memorize syntax, understand when and why to use each command
2. **Practice coding**: Try commands in a Databricks workspace alongside studying
3. **Connect concepts**: Link related cards (e.g., OPTIMIZE + ZORDER + data skipping)
4. **Review documentation**: Use Context7 MCP or official docs for deeper understanding
5. **Hands-on labs**: Create test tables and experiment with different configurations

## 🔗 Additional Resources

- Official Databricks SQL Documentation: https://docs.databricks.com/sql/
- Delta Lake Documentation: https://docs.databricks.com/delta/
- SQL Warehouse API Reference: https://docs.databricks.com/api/workspace/warehouses

## 📝 Card Format Reference

### Basic Cards
```
Front | Back
```

### Cloze Cards
```
Text with {{c1::hidden}} content
```

### Reverse Cards
```
Term | Definition (bidirectional)
```

### Code Cards
```
Question | Code example
```

### Concept Cards
```
Conceptual question | Detailed explanation
```

## 🎯 Learning Objectives

After completing this deck, you should be able to:
- ✅ Create and manage SQL warehouses via UI, CLI, and API
- ✅ Optimize Delta Lake tables for query performance
- ✅ Query historical versions of tables using Time Travel
- ✅ Perform schema evolution operations safely
- ✅ Configure warehouses for cost vs performance trade-offs
- ✅ Understand and apply data skipping techniques
- ✅ Manage table lifecycle with VACUUM and retention policies
- ✅ Choose between partitioning, Z-ordering, and liquid clustering
- ✅ Use Unity Catalog for governance
- ✅ Troubleshoot common performance and configuration issues

---

Generated using Context7 MCP and Claude Code
Date: 2025-10-13
