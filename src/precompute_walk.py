from pathlib import Path          # Path: builds file paths relative to this script
import networkx as nx             # NetworkX: shortest-path calculations on the road graph
import numpy as np                # NumPy: holds the distance table and NaN values
import osmnx as ox                # OSMnx: turns OSM data into a graph of roads
import pandas as pd               # Pandas: reads and writes CSVs

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"

df = (pd.read_csv( PROCESSED/ "hawker_centres_final.csv")           # loads your cleaned hawker centre data
        .dropna(subset=["latitude_hc", "longitude_hc"])               # drops rows with no coordinates (same as the app)
        .reset_index(drop=True))                                      # renumbers rows 0..n-1 so positions line up

G = ox.load_graphml(PROCESSED / "sg_walk_unsimplified.graphml")   # loads the walking network saved by wrangle.py
G = G.to_undirected()                                             # walking is two-way
G = G.subgraph(max(nx.connected_components(G), key=len)).copy()   # keeps the largest connected part

nodes = ox.distance.nearest_nodes(G, X=df["longitude_hc"], Y=df["latitude_hc"])  # snaps each hawker centre to its nearest road node (X = lon, Y = lat)

dist = np.full((len(df), len(df)), np.nan)      # empty n x n table filled with NaN (unknown)

for i, src in enumerate(nodes):                 # loops over each centre as the starting point
    lengths = nx.single_source_dijkstra_path_length(G, src, weight="length")  # shortest walking distance (metres) from this node to every other node
    for j, dst in enumerate(nodes):             # loops over each centre as the destination
        dist[i, j] = lengths.get(dst, np.nan)   # looks up the distance; NaN if no route exists

out = pd.DataFrame(dist, index=df["name"], columns=df["name"]).round(0)   # labels rows and columns with centre names, rounds to whole metres
out.to_csv(PROCESSED / "hawker_centres_walk_distances.csv")  # saves the table under the name the app expects           # saves the table for the app to use
print("Saved", out.shape, "| missing values:", int(out.isna().sum().sum()))  # confirms the size and any gaps