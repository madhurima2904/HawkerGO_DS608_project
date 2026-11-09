from pathlib import Path
import numpy as np
import pandas as pd
import geopandas as gpd
import networkx as nx
import osmnx as ox
from pyrosm import OSM
from pyproj import Transformer
from scipy.spatial import cKDTree 

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"


def load_closures():
    return pd.read_csv(RAW / "DatesofHawkerCentresClosure.csv")


def load_mrt():
    return gpd.read_file(RAW / "LTAMRTStationExitGEOJSON.geojson")


def build_final_table():
    # ---------- Load ----------
    hc_close = pd.read_csv(RAW / "DatesofHawkerCentresClosure.csv")
    mrt = gpd.read_file(RAW / "LTAMRTStationExitGEOJSON.geojson")

    # ---------- Drop unused and text columns ----------
    drop_cols = [
        "serial_no", "remarks_q1", "remarks_q2", "remarks_q3", "remarks_q4",
        "description_myenv", "remarks_other_works", "google_3d_view",
        "google_for_stall", "photourl",
    ]
    hc_close.drop(columns=drop_cols, inplace=True, errors="ignore")

    # ---------- Convert dates and flag TBC ----------
    periods = {
        "q1": ("q1_cleaningstartdate", "q1_cleaningenddate"),
        "q2": ("q2_cleaningstartdate", "q2_cleaningenddate"),
        "q3": ("q3_cleaningstartdate", "q3_cleaningenddate"),
        "q4": ("q4_cleaningstartdate", "q4_cleaningenddate"),
        "other_works": ("other_works_startdate", "other_works_enddate"),
    }
    for key, (start_col, end_col) in periods.items():
        hc_close[f"{key}_tbc"] = (
            hc_close[start_col].astype(str).str.strip().str.upper().eq("TBC")
            | hc_close[end_col].astype(str).str.strip().str.upper().eq("TBC")
        )
        hc_close[start_col] = pd.to_datetime(hc_close[start_col], errors="coerce", dayfirst=True)
        hc_close[end_col] = pd.to_datetime(hc_close[end_col], errors="coerce", dayfirst=True)

    # ---------- Closure length per quarter ----------
    for q in ["q1", "q2", "q3", "q4"]:
        hc_close[f"{q}_days"] = (
            hc_close[f"{q}_cleaningenddate"] - hc_close[f"{q}_cleaningstartdate"]
        ).dt.days + 1

    # ---------- Nearest MRT exit by straight line (metres) ----------
    hc_pts = gpd.GeoDataFrame(
        hc_close,
        geometry=gpd.points_from_xy(hc_close["longitude_hc"], hc_close["latitude_hc"]),
        crs="EPSG:4326",
    )
    mrt_keep = mrt[["STATION_NA", "EXIT_CODE", "geometry"]]

    hc_m = hc_pts.to_crs(epsg=3414).reset_index(drop=True)
    mrt_m = mrt_keep.to_crs(epsg=3414).reset_index(drop=True)

    nearest = gpd.sjoin_nearest(hc_m, mrt_m, how="left", distance_col="dist_to_mrt_m")
    hc_final = nearest[~nearest.index.duplicated(keep="first")].copy()
    hc_final = hc_final.sort_index()

    # ---------- Other works overlapping 2026 ----------
    yr_start, yr_end = pd.Timestamp("2026-01-01"), pd.Timestamp("2026-12-31")
    ow_s = hc_final["other_works_startdate"]
    ow_e = hc_final["other_works_enddate"]

    hc_final["other_works_in_2026"] = (ow_s <= yr_end) & (ow_e >= yr_start)
    hc_final["other_works_days_2026"] = (
        (ow_e.clip(upper=yr_end) - ow_s.clip(lower=yr_start)).dt.days + 1
    ).where(hc_final["other_works_in_2026"])
    hc_final["closed_all_2026"] = (ow_s <= yr_start) & (ow_e >= yr_end)

    # Geometry and index_right are still needed for the walking step
    return hc_final, mrt_m
def add_walking_distances(hc_final, mrt_m):

    # ---------- Load the OpenStreetMap walking network ----------
    singapore_bbox = [103.6, 1.2, 104.1, 1.47]
    osm = OSM(
        str(RAW / "malaysia-singapore-brunei-261018.osm.pbf"),
        bounding_box=singapore_bbox,
    )
    nodes, edges = osm.get_network(network_type="walking", nodes=True)
    G = osm.to_graph(nodes, edges, graph_type="networkx")
    ox.save_graphml(G, filepath=PROCESSED / "sg_walk_unsimplified.graphml")

    # ---------- Largest connected part of the network ----------
    G_u = G.to_undirected()
    G_w = G_u.subgraph(max(nx.connected_components(G_u), key=len)).copy()

    # ---------- KD-tree of graph nodes in metres ----------
    node_ids = np.array(list(G_w.nodes))
    lon = np.array([G_w.nodes[n]["x"] for n in node_ids])
    lat = np.array([G_w.nodes[n]["y"] for n in node_ids])
    tf = Transformer.from_crs(4326, 3414, always_xy=True)
    nx_m, ny_m = tf.transform(lon, lat)
    tree = cKDTree(np.c_[nx_m, ny_m])

    # ---------- Snap each centre and its matched MRT exit ----------
    mrt_geom = mrt_m.geometry.loc[hc_final["index_right"]]
    hc_d, hc_i = tree.query(np.c_[hc_final.geometry.x, hc_final.geometry.y])
    mrt_d, mrt_i = tree.query(np.c_[mrt_geom.x, mrt_geom.y])
    hc_nodes, mrt_nodes = node_ids[hc_i], node_ids[mrt_i]

    # ---------- Walking distance for each pair ----------
    walk = []
    for a, b in zip(hc_nodes, mrt_nodes):
        try:
            walk.append(nx.shortest_path_length(G_w, a, b, weight="length"))
        except nx.NetworkXNoPath:
            walk.append(np.nan)

    hc_final["walk_dist_m"] = np.array(walk) + hc_d + mrt_d
    hc_final["walk_min"] = hc_final["walk_dist_m"] / 80   # about 80 m per minute

    return hc_final
def save_final_table():
    hc_final, mrt_m = build_final_table()
    hc_final = add_walking_distances(hc_final, mrt_m)

    hc_final = hc_final.drop(columns=["index_right", "status", "geometry"])
    PROCESSED.mkdir(parents=True, exist_ok=True)
    hc_final.to_csv(PROCESSED / "hawker_centres_final.csv", index=False)
    print("Saved", hc_final.shape, "to", PROCESSED / "hawker_centres_final.csv")


if __name__ == "__main__":
    save_final_table()