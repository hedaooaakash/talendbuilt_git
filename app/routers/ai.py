from fastapi import APIRouter

from app.models.ai import PromptRequest
from app.ai.pipeline_service import (
    create_pipeline_from_prompt
)

router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)


@router.post("/generate-pipeline")
def generate_pipeline(
    request: PromptRequest
):

    return create_pipeline_from_prompt(
        request.prompt
    )