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

## 59. 회원가입 api 테스트 
테스트 코드를 만들어보자. (다시볼것)

```python
def test_user_sign_up(client, mocker):
    hash_password = mocker.patch.object(
        UserService,
        "hash_password",
        return_value = "hashed"
    )
    user_create = mocker.patch.object(
        User,
        "create",
        return_value = User(id=None, username="test", password="hashed")
    )
    
    mocker.patch.object(
        UserRepository,
        "save_user",
        return_value = User(id=1, username="test", password="hashed")
    )
    
    body = {
        "username": "test",
        "password": "plain"
    }

    response = client.post("/users/sign-up", json=body)
    
    hash_password.assert_called_once_with( # hash_password 메서드가 한번 호출되었는지 확인
        plain_password="plain" 
    )
    
    user_create.assert_called_once_with(
        username="test",
        hashed_password="hashed"
    )
    assert response.status_code == 201
    assert response.json() == {"id": 1, "username": "test"}
```

pytest로 실험해보자.

마지막으로 swagger로도 body를 다음과 같이 입력해서 실험해보자.

```bash
{
    "username": "test",
    "password": "test"
}
```

## 로그인/ 유저 인증 -JWT
JWT: Json Web Token, 사용자 인증에 사용되는 json 포맷의 웹토큰

장점
- 토큰에 유저 정보를 담아 별도의 데이터 조회 없이 인증 처리 가능
- 토큰 변조를 검증할 수 있기 때문에 내장된 데이터 신뢰 가능
- 토큰 만료 가능

인증 절차  
(클라이언트)             (서버)
id & pw             ->  id & pw 검증 / jwt 생성
jwt 저장             ->  jwt 반환(access_token)
api 요청(헤더: jwt)  ->  jwt 검증


## 61. 로그인 API 구현
user.py에 로그인 핸들러를 구현하자.

다음 순서가 될거다.
```python
@router.post("/log-in")
def user_log_in_handler():
    # 1. request body로 username, password 받기
    # 2. DB에서 유저 정보 읽어오기
    # 3. username, password 검증(bcrypt.checkpw)
    # 3. jwt 생성
    # 4. jwt 반환
    return True
```

우선 schema/request.py에 로그인 request body를 정의한다.
```python
class LogInRequest(BaseModel):
    username: str
    password: str
```

그리고 user_log_in_handler 매개변수에 적용

```python
@router.post("/log-in")
def user_log_in_handler(
    request: LogInRequest,
    ):
    # 1. request body로 username, password 받기
    # 2. DB에서 유저 정보 읽어오기
    # 3. username, password 검증(bcrypt.checkpw)
    # 3. jwt 생성
    # 4. jwt 반환
    return True
```

그리고 DB에서 사용자 정보를 읽어오기 위해 repository.py의 UserRepository 클래스에 get_user_by_username 메서드를 정의한다.
```python
class UserRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session
        
    def get_user_by_username(self, username: str) -> User | None:
        return self.session.scalar(
            select(User).where(User.username == username)
            )

    def save_user(self, user: User) -> User:
        self.session.add(instance=user)
        self.session.commit()
        self.session.refresh(instance=user)
        return user
```

그리고 다시 user.py 구현
```python

@router.post("/log-in")
def user_log_in_handler(
    request: LogInRequest,
    user_repo: UserRepository = Depends(),
    ):
    # 1. request body로 username, password 받기
    # 2. DB에서 유저 정보 읽어오기
    user: User | None = user_repo.get_user_by_username(
        username=request.username
        )
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="User Not Found"
            )
    
    # 3. username, password 검증(bcrypt.checkpw)
    # 4. jwt 생성
    # 5. jwt 반환
    return True

```

3번째 user pw 검증 부분 구현은 service/user.py의 UserService에 메서드로 구현하고 가져다 쓰도록 하자.

```python
# service/user.py

import bcrypt

class UserService:
    encoding: str = "UTF-8"
    
    def hash_password(self, plain_password: str) -> str:
        hash_password: bytes = bcrypt.hashpw(
            plain_password.encode(self.encoding), 
            salt=bcrypt.gensalt(),
            )
        return hash_password.decode(self.encoding)
    
    def verify_password(
        self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode(self.encoding),
            hashed_password.encode(self.encoding),
            )
```

이제 이것을 api/user.py에 적용하자.
```python
@router.post("/log-in")
def user_log_in_handler(
    request: LogInRequest,
    user_service: UserService = Depends(),
    user_repo: UserRepository = Depends(),
    ):
    # 1. request body로 username, password 받기
    # 2. DB에서 유저 정보 읽어오기
    user: User | None = user_repo.get_user_by_username(
        username=request.username
        )
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="User Not Found"
            )
    
    # 3. username, password 검증(bcrypt.checkpw)
    verified: bool = user_service.verify_password(
        plain_password=request.password,
        hashed_password=user.password
    )
    if not verified:
        raise HTTPException(
            status_code=401,
            detail="Not Authorized"
            )
    
    # 4. jwt 생성
    # 5. jwt 반환
    return True

```

여기까지 오면 user가 pw 입력까지 잘 성공한 상태다.
로그인을 시켜야한다. jwt 생성 필요...
이를 위해 패키지를 설지하자.
```bash
uv add python-jose
```

그리고 jwt 관련된 작업은 UserService에 추가하자.
```python

class UserService:
    encoding: str = "UTF-8"
    secret_key: str = "secret"
    jwt_algorithm: str = "HS256"
    
    def hash_password(self, plain_password: str) -> str:
        hash_password: bytes = bcrypt.hashpw(
            plain_password.encode(self.encoding), 
            salt=bcrypt.gensalt(),
            )
        return hash_password.decode(self.encoding)
    
    def verify_password(
        self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(
            plain_password.encode(self.encoding),
            hashed_password.encode(self.encoding),
            )

    def create_jwt(self, username: str) -> str:
        return jwt.encode(
            payload=
            { 
                "sub": username,
                "exp": datetime.now() + timedelta(days=1)
            },
            key=self.secret_key,
            algorithm=self.jwt_algorithm
            )
```

그러면 계속해서 api에 jwt 생성부분을 구현하자.
```python

@router.post("/log-in")
def user_log_in_handler(
    request: LogInRequest,
    user_service: UserService = Depends(),
    user_repo: UserRepository = Depends(),
    ):
    # 1. request body로 username, password 받기
    # 2. DB에서 유저 정보 읽어오기
    user: User | None = user_repo.get_user_by_username(
        username=request.username
        )
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="User Not Found"
            )
    
    # 3. username, password 검증(bcrypt.checkpw)
    verified: bool = user_service.verify_password(
        plain_password=request.password,
        hashed_password=user.password
    )
    if not verified:
        raise HTTPException(
            status_code=401,
            detail="Not Authorized"
            )
    
    # 4. jwt 생성
    access_token: str = user_service.create_jwt(
        username=user.username
    )
    # 5. jwt 반환
    return True

```

마지막으로 access_token을 반환하는 부분을 구현하는데, response.py에 정의해서 그것을 사용하자.
```python
class JWTResponse(BaseModel):
    access_token: str
```

그리고 user.py에 반영. 최종 결과는 다음과 같다.
```python

@router.post("/log-in")
def user_log_in_handler(
    request: LogInRequest,
    user_service: UserService = Depends(),
    user_repo: UserRepository = Depends(),
    ):
    # 1. request body로 username, password 받기
    # 2. DB에서 유저 정보 읽어오기
    user: User | None = user_repo.get_user_by_username(
        username=request.username
        )
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="User Not Found"
            )
    
    # 3. username, password 검증(bcrypt.checkpw)
    verified: bool = user_service.verify_password(
        plain_password=request.password,
        hashed_password=user.password
    )
    if not verified:
        raise HTTPException(
            status_code=401,
            detail="Not Authorized"
            )
    
    # 4. jwt 생성
    access_token: str = user_service.create_jwt(
        username=user.username
    )
    # 5. jwt 반환
    return JWTResponse(access_token=access_token)

```

이렇게 하면 클라이언트는 이 액세스 토큰을 이용해서 로그인을 유지한 상태로 API를 호출할수 있음.(하루 기한)


## 62. 로그인 api 테스트
테스트 코드를 짜지않고, swagger ui에서 테스트 해보자.

그전에 현재 db에 저장된 pw가 해시값이 아니라 password 텍스트가 들어가있는 상태다.
따라서 콘솔에서 다음 명령으로 hashed 값을 만들어 주자.

```python

import bcrypt

password = "password".encode("UTF-8")
hashed_password = bcrypt.hashpw(password, salt=bcrypt.gensalt())

hashed_password.decode("UTF-8")
# 아래가 출력됨
'$2b$12$rcj/FV.jRS3d7I26I7OwtOXYt9peGPUxFKwKItZgYNo39zZPqwupq'
```

이제 docker의 mysql에 접속한다.
```
docker exec -it todos bash 
mysql -u root -p

SHOW databases;
USE todos;

select * from user;

update user set password = '$2b$12$rcj/FV.jRS3d7I26I7OwtOXYt9peGPUxFKwKItZgYNo39zZPqwupq' where id = 1;

select * from user;
```

이제 swagger로 확인해보자.
다음 바디를 입력해보자.
```bash
{
  "username": "admin",
  "password": "password"
}
```

결과
```bash
# 200
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2Mjc5NDUwNH0.TEFbpJWtk_cNwMjP6H6kbIuXO-IuFnTrOZfuKMKwRIk"
}
```

## 63. JWT 사용
지금까지 로그인을 통해서 access토큰을 받는 것 까지 구현했다.
이제 access 토큰을 api에서 검증하는 부분을 구현하겠다.
이 것을 구현해서 각 핸들러에 검증하는 로직을 추가하면 된다.


src 아래에 security.py라는 파일을 만들자.
```python
# security.py

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException


# api에서 dependency로 사용할 수 있는 함수 정의

def get_access_token(
    auth_header: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> str:
    if auth_header is None:
        raise HTTPException(
            status_code=401,
            detail="Not Authorized"
            )
    return auth_header.credentials

```

이제 todo.py로 가서 get_todos_hander 함수를 수정해보자.

```python
@router.get("", status_code=200)
def get_todos_handler(
    access_token: str = Depends(get_access_token),
    order: str| None = None,
    todo_repo: ToDoRepository = Depends()
    ) -> ToDoListSchema:
    
    print("======================")
    print(access_token)
    print("======================")
    
    todos: List[ToDo] = todo_repo.get_todos() 
    if order and order == "DESC": 
        return ToDoListSchema(
        todos = [ToDoSchema.model_validate(todo) for todo in todos[::-1]]
    )

    return ToDoListSchema(
        todos = [ToDoSchema.model_validate(todo) for todo in todos]
    )
```


위와 같이 정의하면 api가 호출될때마다, get_access_token 이라는 dependency가 호출이 되서, header에서 bearer 형태로 오는 액세스 토큰이 있나 검증한다. 
없으면 401 에러를 발생시킨다.

만약에 헤더가 정상적으로 요청이 오면 그 안에있는 크레덴셜(access token)을 리턴한다.???

이제 서버를 실행하고, swagger를 실행해서 테스트 해보자.

swagger 오른쪽 위에 authorize가 항목이 있는 것을 알 수 있다.

먼저 로그인 api를 실행해서 access 토큰을 복사해두자.
```bash
{
  "username": "admin",
  "password": "password"
}

# 결과 예시
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2Mjc5NjMwOX0.dKC1nUPyMYaFLJhw0Lmdrpmqf6AZB2jwAJhbASaCYKc"
}
```

이것을 오른쪽 위 httpbearer에 복사 봍여 넣는다.
이렇게 하면 모든 요청에 헤더를 포함하게 된다.

이제 get todos를 실행해보자.
요청할 때 인증 bear가 추가된다.
```bash
curl -X 'GET' \
  'http://127.0.0.1:8000/todos' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc2Mjc5NjMwOX0.dKC1nUPyMYaFLJhw0Lmdrpmqf6AZB2jwAJhbASaCYKc'
```

로그아웃 하고 요청 해보면 401 에러 발생


계속해서 유저 서비스에서 access tocken을 검증하고 user name 꺼내오는 기능을 추가해보자.

그러기위해 우선 user.py 서비스에 decode_jwt라는 함수를 정의 하자.

```python

class UserService:
    encoding: str = "UTF-8"
    secret_key: str = "secret"
    jwt_algorithm: str = "HS256"
    
    def hash_password(self, plain_password: str) -> str:
        hash_password: bytes = bcrypt.hashpw(
            plain_password.encode(self.encoding), 
            salt=bcrypt.gensalt(),
            )
        return hash_password.decode(self.encoding)
...
        
    def decode_jwt(self, access_token: str) -> str:
        payload: dict = jwt.decode(
            access_token,
            self.secret_key,
            algorithms=[self.jwt_algorithm]
            )
        
        return payload["sub"] # username

```

그리고 get todos 핸들러 수정
```python

@router.get("", status_code=200)
def get_todos_handler(
    access_token: str = Depends(get_access_token),
    order: str| None = None,
    user_service: UserService = Depends(),
    user_repo: UserRepository = Depends(),
    todo_repo: ToDoRepository = Depends()
    ) -> ToDoListSchema:
    
    # print("======================")
    # print(access_token)
    # print("======================")
    
    username: str = user_service.decode_jwt(access_token=access_token)
    
    # username을 기반으로 유저 정보를 조회
    user: User | None = user_repo.get_user_by_username(username=username)
    if not user:
        raise HTTPException(status_code=404, detail="User Not Found")
    
    #todos: List[ToDo] = todo_repo.get_todos() 
    todos: List[ToDo] = user.todos
    if order and order == "DESC": 
        return ToDoListSchema(
        todos = [ToDoSchema.model_validate(todo) for todo in todos[::-1]]
    )

    return ToDoListSchema(
        todos = [ToDoSchema.model_validate(todo) for todo in todos]
    )


```

다시 swagger에서 로그인 후 테스트 해볼것

## 64. test_get_todos 코드 변경
jwt를 고려한 테스트 코드 수정

```python
def test_get_todos(client, mocker):
    access_token: str = UserService().create_jwt(username="test")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    user = User(id=1, username="test", password="hashed")
    user.todos = [
        ToDo(id=1, contents="FastAPI Section 0", is_done = True),
        ToDo(id=2, contents="FastAPI Section 1", is_done = False),
    ]
    
    mocker.patch.object(
        UserRepository, 
        "get_user_by_username", 
        return_value = user)

    response = client.get("/todos", headers=headers)
    
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
            {"id": 2, "contents": "FastAPI Section 1", "is_done": False},
        ]
    }    

    # 역순 검증 order=DESC
    response = client.get("/todos?order=DESC", headers=headers) 
    
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 2, "contents": "FastAPI Section 1", "is_done": False},
            {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
        ]
    }    
    

```

## 65. 캐싱
데이터를 임시 저장해서 사용하는 기술

- 장점: 데이터 조회 속도가 빠름. 영속성을 보장할 수 없음
- 임시 데이터, 반복 사용데이터, 빠르게 조회가 필요할 때 사용

OTP: One-Time Password / 일회용 비밀번호

이후 실습에서 회원가입 이후에 OTP를 통해 이메일을 검증하는 기능을 추가해보자.

redis는 Remote Dictionary Serve의 약자임

## 66. Redis 컨테이너 실행 & Redis 연결
Redis: 캐싱에 자주 사용되는 키벨류 데이터 스토어, NoSQL

이제 레디스 컨테이너를 추가하자.
```bash
# 레디스 컨테이너 죽은것이 있으면 지우고 다시 실행하라는 의미
# 포트 번호는 레디스 디펄트 포트번호

docker run -p 6379:6379 --name redis -d --rm redis

```

정상 연결 되는지는 파이썬 라이브러리, 컨솔로 테스트 해보자.

```bash
uv add redis
```

```python
import redis

# redis는 바이트 형테로 데이터 저장함
# 그런데 decode_response True로 설정하면, 바이트가 아니라 파이썬에서 사용하는 데이터 타입으로 변환하여 제공

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0, encoding = "UTF-8", decode_responses=True)

redis_client.set("key", "value")
# True

redis_client.get("key")
# 'value'
```

redis는 만료기능이 있다.
특정 시간동안에만 데이터가 유효하도록 하는 기능.
```python
redis_client.expire("key", 10) # 10초만 유효하도록
```