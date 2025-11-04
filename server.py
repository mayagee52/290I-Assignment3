from fastapi import FastAPI, File, UploadFile
from typing_extensions import Annotated
import uvicorn
from utils import *
from dijkstra import dijkstra

# create FastAPI app
app = FastAPI()

# global variable for active graph
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile):
    import json
    global active_graph
    if not file.filename.lower().endswith(".json"):
        return {"Upload Error": "Invalid file type"}
    try:
        contents = await file.read()
        data = json.loads(contents)

        graph = {}
        for edge in data:
            u, v, w = edge["source"], edge["target"], edge["weight"]
            graph.setdefault(u, {})[v] = w
            if edge.get("bidirectional"):
                graph.setdefault(v, {})[u] = w
        active_graph = graph

        return {"Upload Success": file.filename}
    except Exception:
        return {"Upload Error": "Invalid file type"}


@app.get("/solve_shortest_path/starting_node_id={starting_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(starting_node_id: str, end_node_id: str):
    global active_graph
    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}

    known = set(active_graph.keys())
    for u, nbrs in active_graph.items():
        for v in (nbrs.keys() if isinstance(nbrs, dict) else [n for n, *_ in nbrs]):
            known.add(v)

    if starting_node_id not in known or end_node_id not in known:
        return {"Solver Error": "Invalid start or end node ID."}

    path, total_distance = dijkstra(active_graph, starting_node_id, end_node_id)
    if not path:
        return {"shortest_path": None, "total_distance": None}
    return {"shortest_path": path, "total_distance": total_distance}
    

if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)

    

