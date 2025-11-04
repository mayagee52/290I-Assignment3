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
    global active_graph
    if not file or not file.filename or not file.filename.lower().endswith(".json"):
        return {"Upload Error": "Invalid file type"}
    try:
        raw = await file.read()
        data = json.loads(raw.decode("utf-8"))

        if isinstance(data, dict):
            active_graph = {
                str(u): {str(v): float(w) for v, w in nbrs.items()}
                for u, nbrs in data.items()
            }
        elif isinstance(data, list):
            g = {}
            for e in data:
                u = str(e["source"]); v = str(e["target"]); w = float(e["weight"])
                g.setdefault(u, {})[v] = w
                if e.get("bidirectional"):
                    g.setdefault(v, {})[u] = w
            active_graph = g
        else:
            return {"Upload Error": "Invalid file type"}

        return {"Upload Success": file.filename}
    except Exception:
        return {"Upload Error": "Invalid file type"}

@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    global active_graph
    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}

    known = set(active_graph.keys())
    for _, nbrs in active_graph.items():
        if isinstance(nbrs, dict):
            known.update(nbrs.keys())

    if start_node_id not in known or end_node_id not in known:
        return {"Solver Error": "Invalid start or end node ID."}

    graph_adj = {
        str(u): ([(str(v), float(w)) for v, w in nbrs.items()]
                 if isinstance(nbrs, dict) else nbrs)
        for u, nbrs in active_graph.items()
    }

    try:
        distances, previous = dijkstra(graph_adj, str(start_node_id))
        path = []
        cur = str(end_node_id)
        while cur:
            path.insert(0, cur)
            cur = previous.get(cur)
            if cur == str(start_node_id):
                path.insert(0, cur)
                break

        if not path or path[0] != str(start_node_id):
            return {"shortest_path": None, "total_distance": None}

        total_distance = distances.get(str(end_node_id))
        return {"shortest_path": path, "total_distance": total_distance}
    except Exception as e:
        return {"Solver Error": repr(e)}



if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)


