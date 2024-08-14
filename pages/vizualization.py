import pandas as pd
import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph


def convert_entities_to_nodes(df):
    """Convert the entities dataframe to a list of Node objects for streamlit-agraph."""
    nodes = []
    for _, row in df.iterrows():
        node_id = row["title"]
        nodes.append(
            Node(
                id=node_id,
                label=node_id,
                size=4 + row["size"] * 4,  # Adjust size factor as needed
                color=community_to_color(row["community"]),
            )
        )
    return nodes


def convert_relationships_to_edges(df):
    """Convert the relationships dataframe to a list of Edge objects for streamlit-agraph."""
    edges = []
    for _, row in df.iterrows():
        edges.append(
            Edge(
                source=row["source"],
                target=row["target"],
                title=row.get("description", ""),
                width=row["weight"] * 2,  # Adjust width factor as needed
            )
        )
    return edges


def community_to_color(community):
    """Map a community to a color."""
    colors = [
        "crimson",
        "darkorange",
        "indigo",
        "cornflowerblue",
        "cyan",
        "teal",
        "green",
    ]
    return (
        colors[int(community) % len(colors)] if community is not None else "lightgray"
    )


def visualization():
    with st.container(border=True):
        graph_store_id = st.text_input(
            "GraphStore ID",
            type="password",
            placeholder="gs_****",
        )
    if not (len(graph_store_id) == 27 and graph_store_id.startswith("gs_")):
        return

    input_dir = f"data/graphrag/{graph_store_id}/output/default/artifacts"

    entity_table = "create_final_nodes"
    relationship_table = "create_final_relationships"

    entity_df = pd.read_parquet(f"{input_dir}/{entity_table}.parquet")
    relationship_df = pd.read_parquet(f"{input_dir}/{relationship_table}.parquet")

    nodes = convert_entities_to_nodes(entity_df)
    edges = convert_relationships_to_edges(relationship_df)

    config = Config(
        width=2000,
        height=1000,
        directed=True,
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",  # Highlight color for nodes
        collapsible=True,
    )
    with st.container(border=True):
        agraph(nodes=nodes, edges=edges, config=config)


if __name__ == "__main__":
    st.set_page_config(layout="wide")

    visualization()
