from pydantic import BaseModel
from typing import List


class ToDoSchema(BaseModel): # orm에 생성한 컬럼과 동일일
    id: int
    contents: str
    is_done: bool

    class Config: # 이부분을 추가해주면 pydantic이 ORM 객체를 읽고 알아서 변환해준다.
        from_attributes = True
    

# 이것을 응답에 활용
class ToDoListSchema(BaseModel):
    todos: List[ToDoSchema]
    
    
class UserSchema(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True
        
        
class JWTResponse(BaseModel):
    access_token: str