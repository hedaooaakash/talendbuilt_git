from pydantic import BaseModel

class ConnectionCreate(BaseModel):
    name: str
    type: str
    host: str
    port: int
    username: str
    password: str
    database_name: str