## Fastapi study

- fastapi 설치시 pip install fastapi==0.97.0 명령어를 사용해주세요.

- fastapi 최신 버전을 인스톨 할 경우, fastapi가 pydantic v2를 사용하게 됩니다.

- 강의 제작 시점에는 pydantic v2 공식 버전이 출시되지 않아 본 강좌는 pydantic v1을 기준으로 만들어졌습니다.

 

- 만약 pydantic v2를 사용하고 싶은 분들은 아래 문서를 참고해서 migration을 진행하시면 됩니다.
    - V2 migration: https://docs.pydantic.dev/latest/migration/
 

- fastapi 0.100.0 버전 이상부터 pydantic v2를 공식 지원합니다.

 
- 최종 완성본 프로젝트는 아래의 주소에 공개되어 있습니다.

    - https://github.com/qu3vipon/inflearn-todos



### Status Code
**2xx**
- 200 OK 요청 성공, 범용적, GET/POST/PUT/PATCH
- 201 Created 요청 성공, 새로운 자원 생성, POST
- 204 No Content 요청 성공, 응답할 자원 없음, DELETE

**4xx**
- 400 Bad Request 요청 실패, 요청이 잘못된 경우(query param, body)
- 401 Unauthorized 인증 실패
- 403 Forbidden 권한 문제 또는 잘못된 method
- 404 Not Found 자원이 없는 경우 또는 잘못된 endpoint

**5xx**
- 500 Internal Server Error 범용적인 서버 에러
- 502 Bad Gateway Reverse Proxy에서 서버의 응답을 처리할 수 없는 경우
- 503 Service Unavailable 서버가 요청을 처리할 수 없는 경우(e.g. 일시적 부하, 서버 다운)


## 데이터 베이스
**분류**
- 관계형 데이터베이스(Relational database, RDB)
    - 관계형 모델에 기반해서 데이터를 테이블, 행, 열 구조로 관리(=Schemaful)
    - Oracle, MySQL, PostgreSQL, Sqlite, …
- 비관계형 데이터베이스(NoSQL)
    - Key-value : Redis, etcd
    - Document : MongoDB
    - Wide-column : Cassandra, ScyllaDB
    - Timeseries : Apache Druid,

### Sqlalchemy
**Sqlalchemy**
- 관계형 데이터베이스를 사용하기 위한 High-level 인터페이스를 제공하는 Python 라이브러리
    - ORM, Query, Transaction, Connection Pooling

**ORM(Object-Relational Mapping)**
- 관계형 데이터베이스를 객체 지향 프로그래밍(OOP)에 대응하여 사용하는 프로그래밍 기술
    - 하나의 테이블 = 하나의 클래스
    - 하나의 행(레코드) = 하나의 객체

### 데이터 베이스 실습을 위한 주요 명령어
**Docker 명령어**
```bash
docker run -p 3306:3306 -e MYSQL_ROOT_PASSWORD=todos -e MYSQL_DATABASE=todos -d -v todos:/db --name todos mysql:8.0
docker ps
docker logs todos
docker volume ls
```
 

**MySQL 접속**
```bash
docker exec -it todos bash 
mysql -u root -p
``` 

**SQL**
```bash
SHOW databases;
USE todos;
CREATE TABLE todo(
    id INT NOT NULL AUTO_INCREMENT,
    contents VARCHAR(256) NOT NULL,
    is_done BOOLEAN NOT NULL,
    PRIMARY KEY (id)
);
INSERT INTO todo (contents, is_done) VALUES ("FastAPI Section 0", true);
SELECT * FROM todo;
```


### database/connection.py 생성후 파이썬 터미널에서 테스트
```python

from database.connection import SessionFactory

session = SessionFactory()

from sqlalchemy import select

session.scalar(select(1))
# docker db가 돌아가고 있으면 메시지가 출력됨됨
```

### database/orm.py 생성후 터미널에서 테스트
```python

from database.connection import SessionFactory

session = SessionFactory()

from sqlalchemy import select

from database.orm import ToDo


session.scalars(select(ToDo)) # ToDO에 있는 모든 레코드를 출력함

list(session.scalars(select(ToDo))) # 보기 좋게

```

## 30. ORM 적용한 API 변경하기

우선 connection.py에 get_db()라는 제네레이터를 정의하자.
```python

def get_db():
    session = SessionFactory()
    try:
        yield session
    finally:
        session.close()

```

그리고 repository.py를 만들어 데이터를 조회하는 함수들을 여기에 정의하자.
```python
# ToDo를 리스트에 담아서 리턴
def get_todos(session: Session) -> List[ToDo]:
    return list(session.scalars(select(ToDo)))
```

이제 main.py로 이동해서 get_todos_handler를 수정하자.
```python
@app.get("/todos", status_code=200)
def get_todos_handler(
    order: str| None = None,
    session: Session = Depends(get_db)
    ):
    # result = list(todo_data.values())
    
    todos: List[ToDo] = get_todos(session=session)
    if order and order == "DESC": # DB에서 역정렬 해야지면, 일단 이렇게
        return todos[::-1]
        
    return todos
```

그리고 swagger에서 테스트 해볼것 

### 31. HTTP Response 처리
위 함수는 todos를 리턴하면 fastapi가 자동으로 포맷을 json으로 변경해준다.

하지만 실제에서는 response 포맷을 만들어서 활용한다.

schema라는 디렉토리를 만들자. 거기에 response.py 파일 추가.
여기에 get /todos api가 어떤 형태로 답변해줘야 하는지 정의하자.

```python
class ToDoSchema(BaseModel): # orm에 생성한 컬럼과 동일일
    id: int
    contents: str
    is_done: bool

    class Config: # 이부분을 추가해주면 pydantic이 ORM 객체를 읽고 알아서 변환해준다.
        from_attributes = True
    

# 이것을 응답에 활용
class ListToDoResponse(BaseModel):
    todos: List[ToDoSchema]
```

다시 main.py로 이동하여 def get_todos_handler 수정
```python
@app.get("/todos", status_code=200)
def get_todos_handler(
    order: str| None = None,
    session: Session = Depends(get_db)
    ) -> ListToDoResponse:
    # result = list(todo_data.values())
    
    todos: List[ToDo] = get_todos(session=session)
    if order and order == "DESC": # DB에서 역정렬 해야지면, 일단 이렇게
        return ListToDoResponse(
        todos = [ToDoSchema.model_validate(todo) for todo in todos[::-1]]
    )

    return ListToDoResponse(
        todos = [ToDoSchema.model_validate(todo) for todo in todos]
    )

```

## 32. 단일 조회 Get도 수정해보자.

repository.py에 개별 조회 함수 추가
```python
# 개별 조회, 조회 항목이 없으면 None을 리턴
def get_todo_by_todo_id(session: Session, todo_id: int) -> ToDo | None:
    return session.scalar(select(ToDo).where(ToDo.id == todo_id))
```

main.py에서 get_todo_handler 수정
```python
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
    raise HTTPException(status_code=404, detail="ToDO Not Found")
```

## 33. Refactoring

main.py에 있는 CreateToDoRequest를 schema/resquest.py 파일을 만들고 거기로 이동하자.
```python
# schema/request.py

from pydantic import BaseModel


class CreateToDoRequest(BaseModel):
    id: int
    contents: str
    is_done: bool
```

그리고 response.py에 있는 ListToDoResponse를 ToDoListSchema로 Rename 하자.
```python
class ToDoListSchema(BaseModel):
    todos: List[ToDoSchema]
```

## 34. Post에 ORM 적용하기
POST에 적용할 때는 pydantic 객체를 ORM 객체로 변환해서 적용해야한다.

그러기 위해서, orm.py에 class ToDo에 classmethod를 정의해서 orm 객체로 변환하는 기능을 구현한다.
```python
# orm.py

class ToDo(Base): # mysql에서 생성한 동일한 테이블 구조
    __tablename__ = "todo"
    
    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(256), nullable=False)
    is_done = Column(Boolean, nullable=False)
    
    def __repr__(self): # 내부 정보 출력, 확인위해
        return f"ToDo(id={self.id}, contents={self.contents}, is_done={self.is_done})"
    
    @classmethod
    def create(cls, request: CreateToDoRequest)-> ToDo:
        return cls( # id는 DB에서 별도(자동) 지정되도록 했기 때문에, 두개만 지정하면됨
            contents=request.contents,
            is_done=request.is_done
        )
```

그리고 repository에 DB에 todo를 기록하는 create_todo 함수를 정의하자.
```python

def create_todo(session: Session, todo: ToDo) -> ToDo:
    session.add(instance=todo)
    session.commit() # db에저장
    session.refresh(instance=todo) # 데이터를 다시 읽어주는 부분(db read), 이때 todo_id 값이 반영되서 저장됨
    return todo # id가 포함된 todo를 리턴

```

그리고 request.py에서 CreateToDoRequest의 id를 제외하자. DB에서 자동으로 부여하기 때문이다.
```python
class CreateToDoRequest(BaseModel):
    # id: int
    contents: str
    is_done: bool
```


이제 main.py로 가서 create_todo_handler를 수정하자.
```python
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
```

이제 스웨거에서 post request body를 다음과 같이 추가해보자.
```bash
{
  "contents": "test",
  "is_done": false
}
```

그러면 결과로 자동으로 id 4가 부여된 것을 알 수 있다.
```bash
{
  "id": 4,
  "contents": "test",
  "is_done": false
}
```

## 35. Update, Patch에 ORM 적용

우선 orm.py로 가서 done, undone 메서드를 추가 정의해주자.
```python
class ToDo(Base): # mysql에서 생성한 동일한 테이블 구조
    __tablename__ = "todo"
    
    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(256), nullable=False)
    is_done = Column(Boolean, nullable=False)
    
    def __repr__(self): # 내부 정보 출력, 확인위해
        return f"ToDo(id={self.id}, contents={self.contents}, is_done={self.is_done})"
    
    @classmethod
    def create(cls, request: CreateToDoRequest)-> "ToDo":
        return cls( # id는 DB에서 별도(자동) 지정되도록 했기 때문에, 두개만 지정하면됨
            contents=request.contents,
            is_done=request.is_done
        )
        
    def done(self) -> "ToDo":
        self.is_done = True
        return self
    
    def undone(self) -> "ToDo":
        self.is_done = False
        return self
```

그리고 repository에 update_todo 함수를 정의하자.
```python
# 사실 create_todo와 동일
def update_todo(session: Session, todo: ToDo) -> ToDo:
    session.add(instance=todo)
    session.commit() 
    session.refresh(instance=todo) 
    return todo 
```

이제 main.py의 update_todo_handler를 수정하자.
```python
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
    raise HTTPException(status_code=404, detail="ToDo Not found")
```

이제 swagger에서 patch로 todo_id 3번에 다음과 같이 수정해보자.
```bash
{
  "is_done": true
}
```

결과는 다음과 같다.
```bash
{
  "id": 3,
  "contents": "FastAPI Section 2",
  "is_done": true
}
```

## 36. DELETE에 ORM 적용
먼저 repository.py에 delete_todo 함수 정의
```python
def delete_todo(session: Session, todo_id: int) -> None:
    session.execute(delete(ToDo).where(ToDo.id == todo_id))
    session.commit()
```

main.py를 수정한다.
```python
@app.delete("/todos/{todo_id}", status_code=204)
def delete_todo_handler(
    todo_id: int,
    session: Session = Depends(get_db)
    ):
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="ToDO Not Found")
    
    # delete
    delete_todo(session=session, todo_id=todo_id)
```

swagger를 실행해서 4번 항목을 삭제해보자.
아무런 답변은 없고 204응답만 수신됨