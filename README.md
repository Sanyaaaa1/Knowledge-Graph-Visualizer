# Knowledge Graph Visualizer

A force-directed knowledge graph system that scrapes Wikipedia articles and visualizes their relationships using an interactive physics-based graph in Pygame.

It consists of two main parts:
- A web scraper that builds a graph from Wikipedia links
- A real-time interactive visualizer that renders and explores the graph

---

## Demo

[Watch demo video](https://github.com/Sanyaaaa1/wiki-visualiser/blob/main/videos/vid1.mp4)


## Features

### Scraper
- Crawls Wikipedia starting from a seed article
- Extracts article titles as nodes
- Builds directed edges from hyperlinks between articles
- Filters out non-article pages (special pages, login pages, etc.)
- Outputs a structured JSON graph

### Visualizer
- Force-directed physics simulation (repulsion + spring forces)
- Smooth zoom and pan navigation
- Hover to reveal node connections
- Dynamic layout relaxation over time
- Pause / reset simulation controls
- Lightweight rendering with Pygame

---

## Project Structure

```
storing_project/
│
├── megagraph.json
├── scraper.py
├── visualizer.py
├── videos/
│   └── vid1.mp4
```

---

## Installation

### Requirements

- Python 3.10+
- pip packages:
```
pygame
playwright
```

Install dependencies:

```bash
pip install pygame playwright
playwright install
```

---

## Usage

### 1. Generate Graph Data

```bash
python scraper.py
```

You can change seed and size:

```python
SEED = "https://en.wikipedia.org/wiki/The_Big_Bang_Theory"
scraper = KnowledgeGraphScraper(seed_url=SEED, max_nodes=10)
```

Output:
```
storing_project/megagraph.json
```

---

### 2. Run Visualizer

```bash
python visualizer.py
```

---

## Controls

### Navigation
- Left mouse drag → pan camera
- Mouse wheel → zoom in/out

### Simulation
- SPACE → pause / resume
- R → reset layout

---

## Graph Format

```json
{
  "nodes": [
    { "id": "N1", "label": "Article Title" }
  ],
  "edges_by_node": {
    "N1": ["N2", "N3"]
  }
}
```

Internally converted into adjacency lists.

---

## Physics Model

- Repulsion between all nodes
- Spring forces between linked nodes
- Gravity toward center
- Damping for stability
- Temperature cooling system

---

## Performance Notes

- Optimized repulsion using distance threshold
- Speed limiting per node
- Cooling simulation over time
- Works best for ~100–500 nodes

---

## Ideas for Expansion

- Community detection / clustering
- Search + node focus
- Click-to-pin nodes
- Web version (D3.js / WebGL)
- Path finding between articles
- Multi-graph saving system
