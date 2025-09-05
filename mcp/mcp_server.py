from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import json
from utils.ledger import AuditLedger
from utils.snapshots import SnapshotManager

# Instantiate minimal ledger & snapshots for API usage (shared DB in this demo)
ledger = AuditLedger(db_path="researchmesh_ledger.db")
snapshots = SnapshotManager(ledger=ledger)

app = FastAPI(title="ResearchMesh MCP API (Demo)")

class FetchRequest(BaseModel):
    dataset_id: str
    requester_email: str

class AnalysisRequest(BaseModel):
    dataset_id: str
    snapshot_id: Optional[str] = None

class ShareRequest(BaseModel):
    snapshot_id: str
    channels: list

class ConsentRequest(BaseModel):
    owner_email: str
    requester_email: str
    dataset_id: str
    mode: str

@app.post("/fetch_dataset")
async def fetch_dataset(req: FetchRequest):
    # For demo: return snapshot id after creating snapshot based on role
    # role inference simplified
    role = "external"
    if req.requester_email.endswith("@uni.edu"):
        role = "professor"
    elif req.requester_email.endswith("student.edu"):
        role = "student"
    # naive dataset handling: try to look at snapshots or build a mock
    # Here we create a placeholder snapshot entry
    df = snapshots.get_dataset_sample(req.dataset_id)
    sid = snapshots.save_snapshot(req.dataset_id, df, {"mode": "auto", "requested_by": req.requester_email})
    ledger.log("MCP_API", "fetch_dataset", {"dataset": req.dataset_id, "snapshot": sid, "by": req.requester_email})
    return {"snapshot_id": sid, "mode": "auto"}

@app.post("/run_analysis")
async def run_analysis(req: AnalysisRequest):
    # basic simulation: if snapshot exists, create analysis_result snapshot
    snap = snapshots.get_snapshot(req.snapshot_id) if req.snapshot_id else None
    if snap:
        # store a fake analysis result
        result = {"summary": f"Analysis for {snap['dataset_id']}", "type": "analysis_result"}
        rsid = snapshots.save_snapshot(snap["dataset_id"], snapshots.df_from_object({"result": [json.dumps(result)]}), {"type": "analysis_result"})
        ledger.log("MCP_API", "run_analysis", {"dataset": snap["dataset_id"], "result_snapshot": rsid})
        return {"result_snapshot": rsid, "result": result}
    return {"error": "snapshot not found"}

@app.post("/share_results")
async def share_results(req: ShareRequest):
    snap = snapshots.get_snapshot(req.snapshot_id)
    if not snap:
        return {"error": "snapshot not found"}
    # simulate share
    ledger.log("MCP_API", "share_results", {"snapshot": req.snapshot_id, "channels": req.channels})
    return {"status": "shared", "channels": req.channels}

@app.post("/request_consent")
async def request_consent(req: ConsentRequest):
    cid = f"consent-{len(req.dataset_id)}-{int(len(req.owner_email))}"
    ledger.log("MCP_API", "request_consent", {"consent_id": cid, "owner": req.owner_email, "requester": req.requester_email, "dataset": req.dataset_id})
    return {"consent_id": cid}

def create_app():
    return app
