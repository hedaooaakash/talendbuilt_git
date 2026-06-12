from pydantic import BaseModel

class PipelineStepCreate(BaseModel):
    pipeline_id: int
    step_order: int
    step_type: str
    config_json: str = "{}"