# Section5. 테스트 코드

### 48. FastAPI Router

main.py에서 API 갯수가 커지게 되면 관리가 어려워 진다.
이때는 API를 도메인 별로 또는 자원별로 정리할 필요가 있음


그래서 여기서는 API를 todo 관련 api로 정리하겠음
api 폴더를 만드로 여기에 todo.py를 만들자.

```python
# todo.py


from fastapi import Depends, FastAPI, Body, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.connection import get_db
from database.repository import delete_todo, get_todo_by_todo_id, get_todos, create_todo, update_todo, delete_todo


from database.orm import ToDo
from typing import List

from schema.request import CreateToDoRequest
from schema.response import ToDoListSchema, ToDoSchema
from main import app



@app.get("/todos", status_code=200)
def get_todos_handler(
    order: str| None = None,
    session: Session = Depends(get_db)
    ) -> ToDoListSchema:
    # result = list(todo_data.values())
    
    todos: List[ToDo] = get_todos(session=session)
    if order and order == "DESC": # DB에서 역정렬 해야지면, 일단 이렇게
        return ToDoListSchema(
        todos = [ToDoSchema.model_validate(todo) for todo in todos[::-1]]
    )

    return ToDoListSchema(
        todos = [ToDoSchema.model_validate(todo) for todo in todos]
    )


# 단일 todo를 조회하는 api
@app.get("/todos/{todo_id}", status_code=200)
def get_todo_handler(
    todo_id: int,
    session: Session = Depends(get_db)
    ) -> ToDoSchema:
    # todo = todo_data.get(todo_id)
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)
    if todo:
        # return todo
        return ToDoSchema.model_validate(todo)
    raise HTTPException(status_code=404, detail="ToDo Not Found")

    
# post 메서드를 사용하여 매핑
# pydantic을 사용하여 request body 생성 가능

@app.post("/todos", status_code=201)
def create_todo_handler(
    request: CreateToDoRequest,
    session: Session = Depends(get_db)
    ) -> ToDoSchema:
    #todo_data[request.id] = request.model_dump()
    todo: ToDo = ToDo.create(request=request) # id = None
    todo: ToDo = create_todo(session=session, todo=todo) #id=int
    # return todo_data[request.id]
    return ToDoSchema.model_validate(todo)


@app.patch("/todos/{todo_id}", status_code=200)
def update_todo_handler(
    todo_id: int,
    is_done: bool = Body(..., embed=True),
    session: Session = Depends(get_db)
    ):
    
    # todo = todo_data.get(todo_id)
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)
    if todo: #update
        todo.done() if is_done else todo.undone()
        todo: ToDo = update_todo(session=session, todo=todo)
        return ToDoSchema.model_validate(todo) 
    raise HTTPException(status_code=404, detail="ToDo Not Found")


# delete
@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo_handler(
    todo_id: int,
    session: Session = Depends(get_db)
    ):
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo Not Found")
    
    # delete
    delete_todo(session=session, todo_id=todo_id)


```

이제 이것들을 라우터로 main.py와 연결해야함


우선 router를 선언한고 각 함수의 @app을 다음과 같이 수정

함수들을 라우터와 연결한 것이다.

```python
router = APIRouter()


@router.get("/todos", status_code=200)
....
```

이제 반대로 main.py에서 라우터를 연결해야함.

```python
from api import todo


app = FastAPI()
app.include_router(todo.router)


@app.get("/")
def health_check_handler():
    return {"ping": "pong"}
```

그러면 메인 루트 디렉토리 아래에 헬스체크 api가 있고 그 아래에 todo 라우터들이 있는 구조가 된다.

테스트 코드의 경로도 모두 변경해야한다.
main으로 된것을 api.todo로 변경

```python

def test_get_todos(client, mocker):
    mocker.patch(
        "api.todo.get_todos", # 이부분 수정
        return_value= [
            ToDo(id=1, contents="FastAPI Section 0", is_done = True),
            ...
```

수정하고 pytest 실행해보자.


그리고 다시 todo를 수정해보자.

APIRouter에 prefix를 사용하면 공통경로 삭제 가능


```python
router = APIRouter(prefix="/todos")


@router.get("", status_code=200)

```