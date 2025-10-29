from fastapi import FastAPI, Body
from pydantic import BaseModel

app = FastAPI()

@app.get("/")
def health_check_handler():
    return {"ping": "pong"}


# DB가 없으므로 메모리 데이터를 하나 만들자
todo_data = {
    1: {
        "id": 1,
        "contents": "실전! FastAPI 섹션 0 수강",
        "is_done": True,
    },
    2: {
        "id": 2,
        "contents": "실전! FastAPI 섹션 1 수강",
        "is_done": False,
    },    
    3: {
        "id": 3,
        "contents": "실전! FastAPI 섹션 2 수강",
        "is_done": False,
    },   
}

@app.get("/todos")
def get_todos_handler():
    return list(todo_data.values())


# 쿼리 파라미터
# get 요청 path뒤에 ? 형태로 붙은 파라미터로 추가적인 작업을 가능하도록 함
# fastapi에서는 쿼리 파라미터를 ? 뒤에 붙이는 것이 아니라 함수 인자를 사용해서 전달함
# @app.get("/todos")
# def get_todos_handler(order: str):
#     result = list(todo_data.values())
#     if order == "DESC":
#         return result[::-1] # 역정렬
        
#     return result
# 위경우 http://127.0.0.1:8000/todos?order=DESC를 실행

# order 파라미터를 optional로 받고 싶다면
@app.get("/todos")
def get_todos_handler(order: str| None = None):
    result = list(todo_data.values())
    if order and order == "DESC": # order 값이 있고 order가 DESC라면
        return result[::-1] # 역정렬
        
    return result


# 단일 todo를 조회하는 api
@app.get("/todos/{todo_id}") # 중괄호로 묶어주면 path로 사용가능
def get_todo_handler(todo_id: int):
    return todo_data.get(todo_id, {}) # 없으면 빈딕셔너리 리턴


# post 메서드를 사용하여 매핑
# pydantic을 사용하여 request body 생성 가능
class CreateToDoRequest(BaseModel):
    id: int
    contents: str
    is_done: bool


@app.post("/todos")
def create_todo_handler(request: CreateToDoRequest):
    todo_data[request.id] = request.model_dump() # model_dump 메서드를 사용하면 딕셔너리 포멧으로 변경됨
    return todo_data[request.id]

# patch로 기존 todo update하기: 사용자로부터 완료처리(is_done) 입력 받기
# 앞의 post와 다른점: Request body 전체를 받는 것이 아니라 id와 is_done만 받는다.
@app.patch("/todos/{todo_id}")
def update_todo_handler(
    todo_id: int,
    is_done: bool = Body(..., embed=True) # 하나의 컬럼이지만 바디처럼 묶어서 사용할 수 있음??
    ):
    
    todo = todo_data.get(todo_id)
    if todo:
        todo["is_done"] = is_done
        return todo # 업데이트 결과를 보여줌
    return {} # 없으면 빈 딕셔너리 리턴

# 서버 실행 방법
# uvicorn main:app --reload

# reload: 코드 변경이 감지되면 자동으로 서버 재기동