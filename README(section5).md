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

## 49 의존성 주입
- 다양한 클래스, 함수간 강한 결합을 줄이기 위해 사용되는 기술
- 의존성을 사용하는 컴포넌트가 직접 전달하는 것이 아니라 외부에서 전달(주입)
- injector라고 불리는 별도 모듈에서 관리


## 50.Repository Pattern
- 데이터를 다루는 추상화 기술
- 비즈니스 로직과 데이터 관리의 강한 결합을 완화
- 데이터를 불러오고 저장하는 것 같은 구현을 감출수 있음

이미 여기서 구현됨

todo.py의 get_todos_hander 함수를 보자.
```python
@router.get("", status_code=200)
def get_todos_handler(
    order: str| None = None,
    session: Session = Depends(get_db)
    ) -> ToDoListSchema:
    # result = list(todo_data.values())
    
    todos: List[ToDo] = get_todos(session=session)

    ...
```

repository.py의 get_todos 안에서 데이터를 조회하는 내용을 구현해두었다.

```python
def get_todos(session: Session) -> List[ToDo]:
    return list(session.scalars(select(ToDo)))
```

그런데 지금까지는 레포지터리 패턴을 함수로 정의해두었는데, 클래스로 정의해서 응집력을 높이는 실습을 해보겠다.

repository.py 수정
```python
from fastapi import Depends
from database.connection import get_db

class ToDoRepository:
    def __init__(self, session: Session = Depends(get_db)): # dependency injection 추가
        self.session = session

    def get_todos(self) -> List[ToDo]:
        return list(self.session.scalars(select(ToDo)))

    def get_todo_by_todo_id(self, todo_id: int) -> ToDo | None:
        return self.session.scalar(select(ToDo).where(ToDo.id == todo_id))

    def create_todo(self, todo: ToDo) -> ToDo:
        self.session.add(instance=todo)
        self.session.commit() # db에저장
        self.session.refresh(instance=todo) # 데이터를 다시 읽어주는 부분(db read), 이때 todo_id 값이 반영되서 저장됨
        return todo # id가 포함된 todo를 리턴

    def update_todo(self, todo: ToDo) -> ToDo:
        self.session.add(instance=todo)
        self.session.commit() 
        self.session.refresh(instance=todo) 
        return todo 

    def delete_todo(self, todo_id: int) -> None:
        self.session.execute(delete(ToDo).where(ToDo.id == todo_id))
        self.session.commit()
    
```

이제 실제 이 클래스를 사용하는 부분도 수정해야한다.
todo.py 수정
그리고 타입 힌팅에서 Depends 안의 타입과 힌팅 값이 같은 경우 Depends()로 정의해도 된다.
```python
# 예시
todo_repo: ToDoRepository = Depends()
```

```python
#from database.repository import delete_todo, get_todo_by_todo_id, get_todos, create_todo, update_todo, delete_todo
from database.repository import ToDoRepository

@router.get("", status_code=200)
def get_todos_handler(
    order: str| None = None,
    #session: Session = Depends(get_db) # 이제 세션을 인자로 쓰지 않는다.
    todo_repo: ToDoRepository = Depends() # Depends(TodoRepository)와 같다
    ) -> ToDoListSchema:
    
    todos: List[ToDo] = todo_repo.get_todos() #세션 전달 필요 없음
    if order and order == "DESC": # DB에서 역정렬 해야지면, 일단 이렇게
        return ToDoListSchema(
        todos = [ToDoSchema.model_validate(todo) for todo in todos[::-1]]
    )

    return ToDoListSchema(
        todos = [ToDoSchema.model_validate(todo) for todo in todos]
    )


# 단일 todo를 조회하는 api
@router.get("/{todo_id}", status_code=200)
def get_todo_handler(
    todo_id: int,
    # session: Session = Depends(get_db)
    todo_repo: ToDoRepository = Depends()
    ) -> ToDoSchema:
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if todo:
        # return todo
        return ToDoSchema.model_validate(todo)
    raise HTTPException(status_code=404, detail="ToDo Not Found")

    
# post 메서드를 사용하여 매핑
# pydantic을 사용하여 request body 생성 가능

@router.post("", status_code=201)
def create_todo_handler(
    request: CreateToDoRequest,
    # session: Session = Depends(get_db)
    todo_repo: ToDoRepository = Depends()
    ) -> ToDoSchema:
    #todo_data[request.id] = request.model_dump()
    todo: ToDo = ToDo.create(request=request) # id = None
    todo: ToDo = todo_repo.create_todo(todo=todo) #id=int
    # return todo_data[request.id]
    return ToDoSchema.model_validate(todo)


@router.patch("/{todo_id}", status_code=200)
def update_todo_handler(
    todo_id: int,
    is_done: bool = Body(..., embed=True),
    # session: Session = Depends(get_db)
    todo_repo: ToDoRepository = Depends()
    ):
    # todo = todo_data.get(todo_id)
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if todo: #update
        todo.done() if is_done else todo.undone()
        todo: ToDo = todo_repo.update_todo(todo=todo)
        return ToDoSchema.model_validate(todo) 
    raise HTTPException(status_code=404, detail="ToDo Not Found")


# delete
@router.delete("/{todo_id}", status_code=204)
def delete_todo_handler(
    todo_id: int,
    # session: Session = Depends(get_db)
    todo_repo: ToDoRepository = Depends()
    ):
    todo: ToDo | None = todo_repo.get_todo_by_todo_id(todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo Not Found")
    
    # delete
    todo_repo.delete_todo(todo_id=todo_id)
```

그리고 테스트코드 test_main.py도 수정해야한다.
함수 목킹 부분 수정

이 것도 반영하자.

```python
def test_get_todos(client, mocker):
    # 정상순서 검증
    mocker.patch.object(
        ToDoRepository, 
        "get_todos",
        return_value= [
            ToDo(id=1, contents="FastAPI Section 0", is_done = True),
            ToDo(id=2, contents="FastAPI Section 1", is_done = False),
        ])
    response = client.get("/todos") 
    
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
            {"id": 2, "contents": "FastAPI Section 1", "is_done": False},
        ]
    }    

    # 역순 검증 order=DESC
    response = client.get("/todos?order=DESC") 
    
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 2, "contents": "FastAPI Section 1", "is_done": False},
            {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
        ]
    }    
    
    
    
def test_get_todo(client, mocker):
    # 200
    mocker.patch.object(
        ToDoRepository, 
        "get_todo_by_todo_id", 
        return_value = ToDo(id=1, contents="todo", is_done=True))
    
    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "todo", "is_done": True}
    
    # 400
    mocker.patch.object(
        ToDoRepository, 
        "get_todo_by_todo_id", 
        return_value = None)
    
    response = client.get("/todos/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "ToDo Not Found"}    
    

def test_create_todo(client, mocker):
    create_spy = mocker.spy(ToDo, "create")
    mocker.patch.object(
        ToDoRepository, 
        "create_todo", 
        return_value = ToDo(id=1, contents="todo", is_done=True))
    
    body = {
        "contents": "test",
        "is_done": False
    }
    
    response = client.post("/todos", json = body)
    
    assert create_spy.spy_return.id is None
    assert create_spy.spy_return.contents == "test"
    assert create_spy.spy_return.is_done is False
    
    assert response.status_code == 201
    assert response.json() == {"id": 1, "contents": "todo", "is_done": True}
    
    
def test_update_todo(client, mocker):
    # 200
    mocker.patch.object(
        ToDoRepository, 
        "get_todo_by_todo_id", 
        return_value = ToDo(id=1, contents="todo", is_done=True))
    
    undone = mocker.patch.object(ToDo, "undone")
    
    mocker.patch.object(
        ToDoRepository, 
        "update_todo", 
        return_value = ToDo(id=1, contents="todo", is_done=False))
    
    response = client.patch("/todos/1", json={"is_done": False})
    
    undone.assert_called_once_with()
    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "todo", "is_done": False}
    
    # 404
    mocker.patch.object(
        ToDoRepository, 
        "get_todo_by_todo_id", 
        return_value = None)
    
    response = client.patch("/todos/1", json = {"is_done": True})
    assert response.status_code == 404
    assert response.json() == {"detail": "ToDo Not Found"}        
    
    
def test_delete_todo(client, mocker):
    # 204
    mocker.patch.object(
        ToDoRepository, 
        "get_todo_by_todo_id", 
        return_value = ToDo(id=1, contents="todo", is_done=True))
    
    mocker.patch.object(
        ToDoRepository, 
        "delete_todo", 
        return_value = None)
    
    response = client.delete("/todos/1")
    assert response.status_code == 204
    
    # 404
    mocker.patch.object(
        ToDoRepository, 
        "get_todo_by_todo_id", 
        return_value = None)
    
    response = client.delete("/todos/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "ToDo Not Found"}      
```

