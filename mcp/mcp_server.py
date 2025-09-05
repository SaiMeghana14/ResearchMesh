from fastapi import FastAPI

def create_app():
    app = FastAPI(title="ResearchMesh MCP Server")

    @app.get("/fetch_dataset")
    def fetch_dataset():
        return {"dataset": "sample_datasets.csv"}

    @app.get("/run_analysis")
    def run_analysis():
        return {"status": "analysis complete"}

    @app.get("/share_results")
    def share_results():
        return {"status": "results shared"}

    @app.get("/log_access")
    def log_access():
        return {"status": "access logged"}

    @app.get("/request_consent")
    def request_consent():
        return {"status": "consent granted"}

    return app
