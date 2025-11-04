from fastapi import FastAPI, UploadFile, File
import uvicorn
from utils import create_graph_from_json
from dijkstra import dijkstra

app = FastAPI()
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile = File(...)):
    """Upload a JSON file of edges and build the Graph."""
    global active_graph
    try:
        active_graph = create_graph_from_json(file)
        return {"Upload Success": file.filename, "num_nodes": len(active_graph.nodes)}
    except Exception as e:
        return {"Upload Error": str(e)}


@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    """Run Dijkstra and return shortest path + total distance."""
    global active_graph
    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}

    if start_node_id not in active_graph.nodes or end_node_id not in active_graph.nodes:
        return {"Solver Error": "Start or end node not found in graph."}

    try:
        # Run Dijkstra on your Graph class
        dijkstra(active_graph, active_graph.nodes[start_node_id])

        # reconstruct path
        path = []
        current = active_graph.nodes[end_node_id]
        if current.prev is None and current.id != start_node_id:
            return {"shortest_path": None, "total_distance": None}

        while current is not None:
            path.insert(0, current.id)
            current = current.prev

        total_distance = active_graph.nodes[end_node_id].dist
        return {"shortest_path": path, "total_distance": total_distance}
    except Exception as e:
        return {"Solver Error": str(e)}


if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
