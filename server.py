from fastapi import FastAPI, UploadFile, File
import uvicorn, json
from dijkstra import dijkstra

app = FastAPI()
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}

@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile = File(...)):
    """
    Accepts either:
      - Edge list: [{"source":"u","target":"v","weight":w,"bidirectional":true}, ...]
      - Adjacency dict: {"u": {"v": w, ...}, ...}
    Stores an adjacency dict in global `active_graph`.
    """
    import json
    global active_graph

    raw = await file.read()
    data = json.loads(raw.decode("utf-8"))

    adj = {}

    def add_edge(u, v, w):
        u = str(u); v = str(v)
        adj.setdefault(u, {})
        adj[u][v] = float(w)

    if isinstance(data, list):  # edge list
        for e in data:
            add_edge(e["source"], e["target"], e.get("weight", 1.0))
            if e.get("bidirectional"):
                add_edge(e["target"], e["source"], e.get("weight", 1.0))
    elif isinstance(data, dict):  # adjacency dict
        for u, nbrs in data.items():
            for v, w in nbrs.items():
                add_edge(u, v, w)
    else:
        return {"Upload Error": "Invalid JSON format (use edge list or adjacency dict)."}

    active_graph = adj
    # quick node count (include targets-only)
    nodes = set(adj.keys()) | {v for nbrs in adj.values() for v in nbrs.keys()}
    return {"Upload Success": file.filename, "num_nodes": len(nodes)}


@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    """
    Runs dijkstra(active_graph, start_node_id) and returns the path + total distance.
    """
    global active_graph
    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}

    s, t = str(start_node_id), str(end_node_id)

    # collect all nodes (sources + targets)
    all_nodes = set(active_graph.keys()) | {v for nbrs in active_graph.values() for v in nbrs.keys()}

    if s not in all_nodes:
        return {"Solver Error": f"Start node '{s}' not found."}
    if t not in all_nodes:
        return {"Solver Error": f"End node '{t}' not found."}

    try:
        dist, prev = dijkstra(active_graph, s)  # <-- exactly 2 inputs
    except Exception as e:
        # turn internal errors into a structured response instead of a 500
        return {"Solver Error": f"dijkstra failed: {e!s}"}

    # reconstruct path t -> s via prev
    path = []
    cur = t
    while cur is not None:
        path.insert(0, cur)
        if cur == s:
            break
        cur = prev.get(cur)

    # unreachable or not connected
    if not path or path[0] != s or path[-1] != t:
        return {"shortest_path": None, "total_distance": None}

    # also handle 'inf' or missing distance
    td = dist.get(t)
    if td is None or (isinstance(td, float) and td == float("inf")):
        return {"shortest_path": None, "total_distance": None}

    return {"shortest_path": path, "total_distance": td}


if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)






