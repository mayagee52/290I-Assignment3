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
    try:
        contents = await file.read()
        data = json.loads(contents.decode("utf-8"))

        from graph import Graph
        g = Graph()
        for node, neighbors in data.items():
            for neighbor, weight in neighbors.items():
                g.add_edge(str(node), str(neighbor), float(weight))
        active_graph = g

        return {"Upload Success": file.filename}
    except Exception as e:
        return {"Upload Error": repr(e)}


@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    global active_graph
    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}

    try:
        distances, previous = dijkstra(active_graph, str(start_node_id))
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



