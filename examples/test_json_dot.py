import json
import networkx as nx
from pyvis.network import Network

# 1. Load the JSON data
file_path = "./data/test_graph.json"
with open(file_path, "r") as f:
    data = json.load(f)

# 2. Initialize a Directed Graph in NetworkX
G = nx.DiGraph()

# Add nodes with visual attributes
for node in data["nodes"]:
    G.add_node(node["id"], label=node["label"], color=node.get("color", "#97C2FC"))

# Add edges defining the feedback loops
for edge in data["edges"]:
    G.add_edge(edge["source"], edge["target"])

# 3. Initialize PyVis for a modern browser visualization
# '100%' dimensions fit the screen, directed=True ensures arrows point correctly
net = Network(height="600px", width="100%", directed=True, bgcolor="#ffffff", font_color="#333333")
net.from_nx(G)

# 4. Fine-tune physics specifically for 3-10 node feedback loops
# This prevents loops from overlapping and spaces nodes out beautifully
net.set_options("""
var options = {
  "physics": {
    "barnesHut": {
      "gravitationalConstant": -3000,
      "centralGravity": 0.3,
      "springLength": 95,
      "springConstant": 0.04,
      "damping": 0.09
    },
    "minVelocity": 0.75
  },
  "edges": {
    "smooth": {
      "type": "curvedCW",
      "forceDirection": "none",
      "roundness": 0.2
    }
  }
}
""")

# 5. Generate and open the interactive visualization
net.show("small_feedback_loop.html", notebook=False)
print("Graph generated! Open 'small_feedback_loop.html' in your browser.")
