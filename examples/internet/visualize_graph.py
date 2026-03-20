"""
Graph visualization: Agent ID <-> IP Address
Uses polars for data loading, igraph for graph construction/layout,
and plotly (Scattergl/WebGL) for interactive HTML output.
"""

import os
import polars as pl
import igraph as ig
import plotly.graph_objects as go

LOG_FILE = os.path.join(os.path.dirname(__file__), "internet_logs", "antenna_device_connections.jsonl")
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "graph_interactive.html")


def load_edges(log_file: str) -> pl.DataFrame:
    df = pl.read_ndjson(log_file)
    df = df.filter(pl.col("action") == "connect")
    edges = (
        df.group_by(["agent_id", "agent_name", "ip_address", "device_type", "antenna_id"])
        .len()
        .rename({"len": "weight"})
    )
    return edges


def build_graph(edges: pl.DataFrame) -> ig.Graph:
    agent_ids = edges["agent_id"].unique().to_list()
    ip_addresses = edges["ip_address"].unique().to_list()

    agent_labels = [f"Agent_{aid}" for aid in agent_ids]
    agent_names = {
        row["agent_id"]: row["agent_name"]
        for row in edges.select(["agent_id", "agent_name"]).unique().to_dicts()
    }

    # Node index maps
    agent_idx = {aid: i for i, aid in enumerate(agent_ids)}
    ip_idx = {ip: len(agent_ids) + i for i, ip in enumerate(ip_addresses)}

    # Antenna id per IP (for coloring)
    ip_antenna = {
        row["ip_address"]: row["antenna_id"]
        for row in edges.select(["ip_address", "antenna_id"]).unique().to_dicts()
    }

    n_agents = len(agent_ids)
    n_ips = len(ip_addresses)
    total = n_agents + n_ips

    g = ig.Graph(n=total, directed=False)

    g.vs["node_type"] = ["agent"] * n_agents + ["ip"] * n_ips
    g.vs["label"] = (
        [agent_names.get(aid, f"Agent_{aid}") for aid in agent_ids]
        + list(ip_addresses)
    )
    g.vs["agent_id"] = agent_ids + [None] * n_ips
    g.vs["antenna_id"] = [None] * n_agents + [ip_antenna[ip] for ip in ip_addresses]

    edge_list = []
    weights = []
    device_types = []
    for row in edges.to_dicts():
        src = agent_idx[row["agent_id"]]
        dst = ip_idx[row["ip_address"]]
        edge_list.append((src, dst))
        weights.append(row["weight"])
        device_types.append(row["device_type"])

    g.add_edges(edge_list)
    g.es["weight"] = weights
    g.es["device_type"] = device_types

    return g


def antenna_color(antenna_id, all_antenna_ids: list) -> str:
    """Map antenna_id to a hue in red/orange range."""
    if antenna_id is None:
        return "#e74c3c"
    unique_sorted = sorted(set(all_antenna_ids))
    idx = unique_sorted.index(antenna_id)
    # Hue: interpolate from 0 (red) to 30 (orange) degrees
    ratio = idx / max(1, len(unique_sorted) - 1)
    r = 255
    g_val = int(80 + ratio * 100)
    b = int(50 + ratio * 50)
    return f"rgb({r},{g_val},{b})"


def render_plotly(g: ig.Graph, output_file: str):
    print("Computing layout (Fruchterman-Reingold)...")
    import random
    random.seed(42)
    layout = g.layout_fruchterman_reingold(weights=g.es["weight"])
    coords = layout.coords  # list of (x, y)

    xs = [c[0] for c in coords]
    ys = [c[1] for c in coords]

    all_antenna_ids = [v["antenna_id"] for v in g.vs if v["node_type"] == "ip"]

    # --- Edge trace ---
    edge_x, edge_y = [], []
    for edge in g.es:
        x0, y0 = coords[edge.source]
        x1, y1 = coords[edge.target]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scattergl(
        x=edge_x,
        y=edge_y,
        mode="lines",
        line=dict(width=0.5, color="#aaaaaa"),
        hoverinfo="none",
        name="Connection",
    )

    # --- Agent nodes ---
    agent_vs = [v for v in g.vs if v["node_type"] == "agent"]
    agent_trace = go.Scattergl(
        x=[xs[v.index] for v in agent_vs],
        y=[ys[v.index] for v in agent_vs],
        mode="markers",
        marker=dict(size=10, color="#2980b9", line=dict(width=1, color="white")),
        text=[v["label"] for v in agent_vs],
        textposition="top center",
        textfont=dict(size=9, color="#2980b9"),
        customdata=[v["agent_id"] for v in agent_vs],
        hovertemplate="<b>%{text}</b><br>Agent ID: %{customdata}<extra></extra>",
        name="Agent",
    )

    # --- IP nodes ---
    ip_vs = [v for v in g.vs if v["node_type"] == "ip"]
    ip_colors = [antenna_color(v["antenna_id"], all_antenna_ids) for v in ip_vs]
    ip_trace = go.Scattergl(
        x=[xs[v.index] for v in ip_vs],
        y=[ys[v.index] for v in ip_vs],
        mode="markers",
        marker=dict(size=6, color=ip_colors, line=dict(width=0.5, color="white")),
        text=[v["label"] for v in ip_vs],
        textposition="bottom center",
        textfont=dict(size=8, color="#c0392b"),
        customdata=[v["antenna_id"] for v in ip_vs],
        hovertemplate="<b>IP: %{text}</b><br>Antenna: %{customdata}<extra></extra>",
        name="IP Address",
    )

    fig = go.Figure(
        data=[edge_trace, agent_trace, ip_trace],
        layout=go.Layout(
            title="Agent ID ↔ IP Address Graph",
            showlegend=True,
            hovermode="closest",
            dragmode="pan",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor="white",
            legend=dict(itemsizing="constant"),
        ),
    )

    # JavaScript: show labels only when zoomed in enough
    post_script = """
    var gd = document.querySelector('.js-plotly-plot');
    var initialXRange = null;

    gd.on('plotly_afterplot', function() {
        if (initialXRange === null) {
            initialXRange = Math.abs(gd.layout.xaxis.range[1] - gd.layout.xaxis.range[0]);
        }
    });

    gd.on('plotly_relayout', function(ed) {
        if (initialXRange === null) return;
        var xr = gd.layout.xaxis.range;
        if (!xr) return;
        var currentWidth = Math.abs(xr[1] - xr[0]);
        var showLabels = currentWidth < initialXRange * 0.35;
        var newMode = showLabels ? 'markers+text' : 'markers';
        // traces 1 = agents, 2 = IP nodes
        Plotly.restyle(gd, {mode: newMode}, [1, 2]);
    });
    """

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    fig.write_html(output_file, post_script=post_script)
    print(f"Saved: {output_file}")


def main():
    print("Loading data...")
    edges = load_edges(LOG_FILE)
    print(f"  {len(edges)} unique agent-IP pairs, "
          f"{edges['agent_id'].n_unique()} agents, "
          f"{edges['ip_address'].n_unique()} IPs")

    print("Building graph...")
    g = build_graph(edges)
    print(f"  {g.vcount()} nodes, {g.ecount()} edges")

    render_plotly(g, OUTPUT_FILE)


if __name__ == "__main__":
    main()
