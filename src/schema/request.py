from pydantic import BaseModel


class CreateToDoRequest(BaseModel):
    # id: int
    contents: str
    is_done: bool
    

class SignUpRequest(BaseModel):
    username: str
    password: str