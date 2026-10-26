from pathlib import Path          # Path: builds file paths relative to this script
import networkx as nx             # NetworkX: shortest-path calculations on the road graph
import numpy as np                # NumPy: holds the distance table and NaN values
import osmnx as ox                # OSMnx: turns OSM data into a graph of roads
import pandas as pd               # Pandas: reads and writes CSVs

root = Path(__file__).parent      # the folder this script lives in

df = (pd.read_csv(root / "data-processed" / "hawker_centres_final.csv")           # loads your cleaned hawker centre data
        .dropna(subset=["latitude_hc", "longitude_hc"])               # drops rows with no coordinates (same as the app)
        .reset_index(drop=True))                                      # renumbers rows 0..n-1 so positions line up

G = ox.graph_from_xml(                          # builds the road network graph from the file
    root / "data-raw" / "sg_roads.osm",         # the filtered Singapore roads file
    bidirectional=True,                         # pedestrians can walk both ways on every road
    simplify=True,                              # merges nodes along straight stretches to speed things up
    retain_all=False,                           # keeps only the largest connected network, dropping isolated bits
)

nodes = ox.distance.nearest_nodes(G, X=df["longitude_hc"], Y=df["latitude_hc"])  # snaps each hawker centre to its nearest road node (X = lon, Y = lat)

dist = np.full((len(df), len(df)), np.nan)      # empty n x n table filled with NaN (unknown)

for i, src in enumerate(nodes):                 # loops over each centre as the starting point
    lengths = nx.single_source_dijkstra_path_length(G, src, weight="length")  # shortest walking distance (metres) from this node to every other node
    for j, dst in enumerate(nodes):             # loops over each centre as the destination
        dist[i, j] = lengths.get(dst, np.nan)   # looks up the distance; NaN if no route exists

out = pd.DataFrame(dist, index=df["name"], columns=df["name"]).round(0)   # labels rows and columns with centre names, rounds to whole metres
out.to_csv(root / "data-processed" / "hawker_centres_walk_distances.csv")  # saves the table under the name the app expects           # saves the table for the app to use
print("Saved", out.shape, "| missing values:", int(out.isna().sum().sum()))  # confirms the size and any gaps