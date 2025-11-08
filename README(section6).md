# 6. 기능 고도화
- ToDO 서비스의 회원가입 기능 추가
- 테이블 조인, 캐싱, 백그라운드 태스크 기술 

## 51. SQL 조인
- 공통되는 컬럼을 이용하여 도개 테이블을 연결해서 조회하는 기능

User
id | username 
1 | qu3vipon

ToDo
id | user_id | contents
1 | 1 | FastAPI Section 1
2 | 1 | FastAPI Section 2

```SQL
SELECT u.username, t.contents FROM user u JOIN todo t ON u.id = t.user_id;
```

username | contents
qu3vipon | FastAPI Section 1
qu3vipon | FastAPI Section 2

## 52. User 모델링
- sql alchemy로 유저 테이블을 모델링
- 모델링한 코드를 기반으로 MySQL의 유저 테이블을 실제로 생성해 주자.

먼저 sqlalchemy의 특징 확인을 위해 파이썬 콘솔을 열어서 다음을 입력해보자.

```python
from sqlalchemy.schema import CreateTable
from database.orm import ToDo
from database.connection import engine

print(CreateTable(ToDo.__table__).compile(engine))

# 결과
CREATE TABLE todo (
        id INTEGER NOT NULL AUTO_INCREMENT, 
        contents VARCHAR(256) NOT NULL, 
        is_done BOOL NOT NULL, 
        PRIMARY KEY (id)
)
```

테이블 생성 SQL이 자동 생성된다.
클래스를 모델링하면 생성 SQL이 자동 생성할 수 있다.

이 것을 활용해서 만들어보자.

orm.py에 유저 테이블 클래스를 만들자.

```python
class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), nullable=False)
    password = Column(String(256), nullable=False)
```

그리고 join을 하기위해 기존에 만들었던 todo 테이블에 foreign 키를 추가하자.
```python
class ToDo(Base): # mysql에서 생성한 동일한 테이블 구조
    __tablename__ = "todo"
    
    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(256), nullable=False)
    is_done = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id")) # 외래 키 추가
    ...
```

이제 파이썬 콘솔을 실행한 후 다음을 입력하자.

```python

from sqlalchemy.schema import CreateTable
from database.orm import ToDo, User
from database.connection import engine

print(CreateTable(User.__table__).compile(engine))

# 결과
CREATE TABLE user (
        id INTEGER NOT NULL AUTO_INCREMENT, 
        username VARCHAR(256) NOT NULL, 
        password VARCHAR(256) NOT NULL, 
        PRIMARY KEY (id)
)
```

뒤에서 user table 생성을 위해서는 sqlalchemy 함수를 쓸거다.  
그런데 기존 ToDo 테이블은 user_id 컬럼만 추가할 것이기 때문에 테이블을 생성하지 않고 alter table 명령어를 써서 컬럼을 추가할 거다.

## 53. 테이블 관련 쿼리
```sql
CREATE TABLE user (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    username VARCHAR(256) NOT NULL, 
    password VARCHAR(256) NOT NULL, 
    PRIMARY KEY (id)
);

ALTER TABLE todo ADD COLUMN user_id INTEGER;

ALTER TABLE todo ADD FOREIGN KEY(user_id) REFERENCES user (id);

INSERT INTO user (username, password) VALUES ("admin", ”password”);

UPDATE todo SET user_id = 1 WHERE id = 1;

SELECT * FROM todo t JOIN user u ON t.user_id = u.id;
```

## 54. User 테이블 생성

Docker my sql에 접속해서 user 테이블을 생성하자.

컨테이너 bash 실행
```bash
docker exec -it todos bash
```

root 유저로 mysql 실행
```bash
mysql -u root -p
# pw: todos
```

```sql
# todos DB로 이동
use todos;

# 데이터 조회
select * from todo;
+----+-------------------+---------+
| id | contents          | is_done |
+----+-------------------+---------+
|  1 | FastAPI Section 0 |       1 |
|  2 | FastAPI Section 1 |       1 |
|  3 | FastAPI Section 2 |       1 |
+----+-------------------+---------+
3 rows in set (0.00 sec)

# user 테이블 생성
CREATE TABLE user (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    username VARCHAR(256) NOT NULL, 
    password VARCHAR(256) NOT NULL, 
    PRIMARY KEY (id)
);

# 확인
select * from user;

Empty set (0.00 sec)
```

todo 테이블 수정, 연결
```sql
ALTER TABLE todo ADD COLUMN user_id INTEGER;

# 확인
select * from todo;
+----+-------------------+---------+---------+
| id | contents          | is_done | user_id |
+----+-------------------+---------+---------+
|  1 | FastAPI Section 0 |       1 |    NULL |
|  2 | FastAPI Section 1 |       1 |    NULL |
|  3 | FastAPI Section 2 |       1 |    NULL |
+----+-------------------+---------+---------+
3 rows in set (0.00 sec)

# user_id와 user 테이블의 id 연결
ALTER TABLE todo ADD FOREIGN KEY(user_id) REFERENCES user (id);

# 실습을 위해 user 테이블에 값 하나 추가(pw는 해시룰 추가해야하나 여기서는 그냥 추가)
INSERT INTO user (username, password) VALUES ("admin", ”password”);

# 확인
select * from user;
+----+----------+----------+
| id | username | password |
+----+----------+----------+
|  1 | admin    |          |
+----+----------+----------+
1 row in set (0.00 sec)

# user_id와 id 값이 매핑이 안되어 있다. 그래서 강제 매핑
UPDATE todo SET user_id = 1 WHERE id = 1;
UPDATE todo SET user_id = 1 WHERE id = 2;
UPDATE todo SET user_id = 1 WHERE id = 3;

# 확인
select * from todo;
+----+-------------------+---------+---------+
| id | contents          | is_done | user_id |
+----+-------------------+---------+---------+
|  1 | FastAPI Section 0 |       1 |       1 |
|  2 | FastAPI Section 1 |       1 |       1 |
|  3 | FastAPI Section 2 |       1 |       1 |
+----+-------------------+---------+---------+
3 rows in set (0.00 sec)

# 조인 해보기
SELECT * FROM todo t JOIN user u ON t.user_id = u.id;

# 확인
+----+-------------------+---------+---------+----+----------+----------+
| id | contents          | is_done | user_id | id | username | password |
+----+-------------------+---------+---------+----+----------+----------+
|  1 | FastAPI Section 0 |       1 |       1 |  1 | admin    |          |
|  2 | FastAPI Section 1 |       1 |       1 |  1 | admin    |          |
|  3 | FastAPI Section 2 |       1 |       1 |  1 | admin    |          |
+----+-------------------+---------+---------+----+----------+----------+
3 rows in set (0.00 sec)
```

## 55. ORM Join
앞으로 user를 조회할때 마다 user의 todo도 함께 조회하려고 한다.
그러기 위해서는 user 클래스에 todo 속성을 연결해야한다.

```python
class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), nullable=False)
    password = Column(String(256), nullable=False)
    todos = relationship("ToDo", lazy="joined") # 컬럼이 생성되는 것이 아니라 쿼리가 실행될 때 조인된 결과를 가져옴

```

이렇게 하면 user.todo 같은 명령으로 user의 전체 todo를 조회할수 있게 된다.

## 56. Lazy Loading/ Eager loading
- Lazy Loading: 지연 로딩 연관된 객체의 데이터가 실제로 필요한 시점에 조회하는 방법
    - 장점: 첫 조회 속도가 더 빠름
    - 단점: N+1 문제 발생

- N+1 Problem: 반복문을 사용할 때는 반복문 횟수만큼 조인이 발생
```python
for todo in todos:
    print(todo.user.username)
```

- Eager Loading: 즉시 로딩 데이터를 조회할 때 처음부터 연관된 객체를 같이 읽어오는 방법
    - 장점: 데이터를 더 효율적으로 가져올 수 있음(N+1 방지)
    - 단점: 꼭 필요하지 않은 데이터까지 JOIN 해서 읽어올 수 있음

## 57 회원 가입 API 생성 및 비번 암호화
api 폴더에 user.py를 만들자.
일단 내용은 빼고 함수와 라우터만 정의해둠.
```python
# user.py
from fastapi import APIRouter

router = APIRouter(prefix="/users")

@router.post("/sign-up")
def user_sign_up_handler():
    return True

```

그리고 main.py에 와서 라우터 추가

```python
from api import todo, user


app = FastAPI()
app.include_router(todo.router)
app.include_router(user.router)
```

api가 잘 연동되었는지 테스트 코드 작성, 실행

그전에 test_main.py를 리네임해주고 파일도 나눠주자.
api가 나누어 졌기 때문에 나누어 주는 것이 맞을 듯.

test_main.py, test_todos_api.py, test_users_api.py 세개로 나눈다.

```python
# test_main.api
def test_health_check(client):
    response = client.get("/") # 이방식으로 앱에 get요청, 결과를 response에 저장
    
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
```

```python
# test_todos_api.api
from fastapi.testclient import TestClient

from database.orm import ToDo
from main import app
from database.repository import ToDoRepository

def test_get_todos(client, mocker):
    # 정상순서 검증
    mocker.patch.object(
        ToDoRepository, 
        "get_todos",

....
```

```python
# test_users_api.py

def test_user_sign_up(client):
    response = client.post("/users/sign-up")
    assert response.status_code == 200
    assert response.json() is True
```
위처럼 하고 pytest로 api만 간단하게 우선 테스트 해보자.

이제 실제 테스트 코드를 작성하자.

다음과 같이 만들거다.

```python
@router.post("/sign-up", status_code=201)
def user_sign_up_handler():
    # 1. request body로 username, password 받기
    # 2. password -> hassing -> hassed_password
    # 4. user -> db insert
    # 5. return user(id, username) # pw는 알려주면 안되기 때문에
    return True
```

그전에 해싱에 대해서 알아보자.
비밀번호 암호화를 위해 bcrypt라는 패키지 필요
```bash
uv add bcrypt
```

이제 파이썬 컨솔을 실행해서 테스트 해보자.
```python
import bcrypt

password = "password"

# 패스워드 암호와

# 비크립트는 암호와를 위해 패스워드를 byte로 바꿔조야함
# 여기서는 utf-8로 바이트 인코딩을 해줌
byte_password = password.encode("UTF-8")

hash_1 = bcrypt.hashpw(byte_password, salt=bcrypt.gensalt())
hash_2 = bcrypt.hashpw(byte_password, salt=bcrypt.gensalt())

# 일반적인 해시는 항상 동일한 것을 생성.
# 하지만 솔트를 사용하면 그때그때 달라진다.
hash_1 == hash_2 # False가 출력됨

# 검증방법
bcrypt.checkpw(byte_password, hash_1) # True 출력
bcrypt.checkpw(byte_password, hash_2) # True 출력됨
```

## 58. 회원가입 API 구현
이제 본격적으로 Sign up api 구현

우선 schema/request.py에다가 signup request body를 정의하자.

```python
# request.py

class SignUpRequest(BaseModel):
    username: str
    password: str
```

그리고 api에 request body를 추가
```python
# user.py

from fastapi import APIRouter
from schema.request import SignUpRequest

router = APIRouter(prefix="/users")

@router.post("/sign-up", status_code=201)
def user_sign_up_handler(request: SignUpRequest):

    ....
```

그런데 hash는 별도의 클래스로 뺄것이다.
service/user.py를 만들고 여기에 정의하자.

```python
# user.py

import bcrypt

class UserService:
    encoding: str = "UTF-8"
    
    def hash_password(self, plain_password: str) -> str:
        hash_password: bytes = bcrypt.hashpw(
            plain_password.encode(self.encoding), 
            salt=bcrypt.gensalt(),
            )
        return hash_password.decode(self.encoding)

```

그리고 다시 api/user.py로 가서 Depends로 이 클래스를 불러오자.
그리고 해시 처리하는 코드도 구현
```python
@router.post("/sign-up", status_code=201)
def user_sign_up_handler(
    request: SignUpRequest,
    user_service: UserService = Depends(),
    ):
    # 1. request body로 username, password 받기
    # 2. password -> hassing -> hassed_password
    hashed_password: str = user_service.hash_password(
        plain_password=request.password
        )
        ...
```

다음으로 User를 만들건데 orm.py에 있는 User 클래스에 class 메서드를 만들고, 이것을 호출해서 사용하자.
그래서 우선 클래스 메서드를 만들자.

```python
# orm.py

class User(Base):
    __tablename__ = "user"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), nullable=False)
    password = Column(String(256), nullable=False)
    todos = relationship("ToDo", lazy="joined") # 컬럼이 생성되는 것이 아니라 쿼리가 실행될 때 조인된 결과를 가져옴

    @classmethod
    def create(cls, username: str, hashed_password: str) -> "User":
        return cls(
            username=username,
            password=hashed_password
        )

```

그리고 다시 돌아가서 구현...

```python
@router.post("/sign-up", status_code=201)
def user_sign_up_handler(
    request: SignUpRequest,
    user_service: UserService = Depends(),
    ):
    # 1. request body로 username, password 받기
    # 2. password -> hassing -> hassed_password
    hashed_password: str = user_service.hash_password(
        plain_password=request.password
        )
    
    # 3. User(usernam, hashed_password)
    user: User = User.create(
        username=request.username,
        hashed_password=hashed_password
    )
    
    # 4. user -> db insert
    # 5. return user(id, username) # pw는 알려주면 안되기 때문에
    return True
```

이제 db 저장 부분을 구현해야하는데, repository.py에 UserRepository 클래스를 구현해서 사용하자.

```python
# database/repository.py

class UserRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session

    def save_user(self, user: User) -> User:
        self.session.add(instance=user)
        self.session.commit()
        self.session.refresh(instance=user)
        return user

```

다시 user.py로 와서 저장하는 부분 구현

```python
@router.post("/sign-up", status_code=201)
def user_sign_up_handler(
    request: SignUpRequest,
    user_service: UserService = Depends(),
    user_repo: UserRepository = Depends(),
    ):
    # 1. request body로 username, password 받기
    # 2. password -> hassing -> hassed_password
    hashed_password: str = user_service.hash_password(
        plain_password=request.password
        )
    
    # 3. User(usernam, hashed_password)
    user: User = User.create(
        username=request.username,
        hashed_password=hashed_password
    ) # 이시점에는 user의 id가 None이다. orm 객체로만 있는 상태
    
    # 4. user -> db insert
    user: User = user_repo.save_user(user=user) # 이시점에는 user의 id가 int이다. orm 객체가 db에 저장되고 다시 읽어와서 반영된 상태
    
    
    # 5. return user(id, username) # pw는 알려주면 안되기 때문에
    return True
```

마지막으로 return 정보를 구현허는데, respone.py에 스키마를 정의해서 사용하자.

```python

class UserSchema(BaseModel):
    id: int
    username: str
    
    class Config:
        from_attributes = True

```

이제 리턴 정보까지 구현한 최종 형태.

```python
# user.py

@router.post("/sign-up", status_code=201)
def user_sign_up_handler(
    request: SignUpRequest,
    user_service: UserService = Depends(),
    user_repo: UserRepository = Depends(),
    ):
    # 1. request body로 username, password 받기
    # 2. password -> hassing -> hassed_password
    hashed_password: str = user_service.hash_password(
        plain_password=request.password
        )
    
    # 3. User(usernam, hashed_password)
    user: User = User.create(
        username=request.username,
        hashed_password=hashed_password
    ) # 이시점에는 user의 id가 None이다. orm 객체로만 있는 상태
    
    # 4. user -> db insert
    user: User = user_repo.save_user(user=user) # 이시점에는 user의 id가 int이다. orm 객체가 db에 저장되고 다시 읽어와서 반영된 상태
    
    
    # 5. return user(id, username) # pw는 알려주면 안되기 때문에
    return UserSchema.model_validate(user)


```