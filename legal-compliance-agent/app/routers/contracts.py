from fastapi import APIRouter, UploadFile, File
from ..models.schemas import ContractReviewResponse
from ..services.contracts import review_contract_file
import tempfile, os

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

@router.post("/review", response_model=ContractReviewResponse)
async def review(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename)[1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    extracted, risks, report_path = review_contract_file(tmp_path)
    os.remove(tmp_path)
    return {
        "extracted": extracted,
        "diff_against": "baseline_v1",
        "risks": risks,
        "report_url": f"file://{report_path}"
    }
