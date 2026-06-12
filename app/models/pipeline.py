from pydantic import BaseModel

class PipelineCreate(BaseModel):
    name: str
    description: str
    source_type: str
    target_type: str