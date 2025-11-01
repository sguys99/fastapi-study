# Section4. 테스트 코드

테스트 코드
- 시스템의 품질과 신뢰성을 검증하기 위한 코드

장점
- ‘코드 변경 -> 기능 점검’ 과정 자동화 => 반복적인 과정을 줄여주어 생산성 향상
- 개발자가 시스템에 대한 안정성 확신 => 유연한 코드 변경 및 리팩터링

심화
- Unit Test, Integration Test, Regression Test, TDD, BDD 등 다양한 테스트 종류와 방법론 존재

Pytest: 테스트 코드 작성을 위한 라이브러리



## 40. pytest 세팅
```bash
uv add pytest
uv add httpx
```

이제 test라는 패키지(__init__.py가 포함된 디렉토리를 생성한다.)

그리고 거기에 test_main.py를 만들어준다.

네이밍 컨벤션 test_파일이름 형태를 맞춰주면 pytest가 알아서 테스트 파일을 찾아준다.

여기에 health check 메서드에 대한 테스트 코드를 작성해보자.
```python
from fastapi.testclient import TestClient

from main import app


client = TestClient(app=app) # 우리가 만든 app이 테스트 클라이언트가 되서 테스트를 진행하는 방식

def test_health_check():
    response = client.get("/") # 이방식으로 앱에 get요청, 결과를 response에 저장
    
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
```

테스트를 할때는 pytest 라고 터미널에서 입력을 하면 알아서 디렉토리를 찾고 테스트를 진행한다.

```bash
pytest
```
몇번 실행하다고 꼬이거나 동작안하면 .pytest_cache 파일을 삭제하고 다시 진행한다.


## 41. 전체 To Do를 조회하는 get_todos_handler 테스트 코드 추가
```python
def test_get_todos():
    # 정상순서 검증
    response = client.get("/todos") 
    
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
            {"id": 2, "contents": "FastAPI Section 1", "is_done": True},
            {"id": 3, "contents": "FastAPI Section 2", "is_done": True},
        ]
    }    

    # 역순 검증 order=DESC
    response = client.get("/todos?order=DESC") 
    
    assert response.status_code == 200
    assert response.json() == {
        "todos": [
            {"id": 3, "contents": "FastAPI Section 2", "is_done": True},
            {"id": 2, "contents": "FastAPI Section 1", "is_done": True},
            {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
        ]
    }  
```
이후 pytest 명령으로 실행

## 42. Pytest mocking

그런데 위 테스트 코드는 문제가 있다.
테스트 동안 데이터 베이스 2번 조회함
데이터 조회에는 문제가 없지만 생성하거나 업데이트를 하면 변경을 발생시킴
실제 DB에 접근하지 않고 마치 접근하는 것처럼 속이는 mocking 이란 것을 사용해보자.

라이브러리 추가 필요
```
uv add pytest-mock
```

mocking을 사용할때는 함수에 mocker라는 항목 추가하면 됨

```python
# mocking 반영
def test_get_todos(mocker):
    # 정상순서 검증
    mocker.patch(
        "main.get_todos", # get_todos_handler 함수 안에서 호출되는 get_todos를 모킹하겠다는 의미
        return_value= [
            ToDo(id=1, contents="FastAPI Section 0", is_done = True),
            ToDo(id=2, contents="FastAPI Section 1", is_done = False),
        ]) # 실제와 동일하게 리턴 값을 적을 필요가 없다.
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
```

## 43. pytest fixture

함수안의 객체가 있을 떄 그 데이터나 객체를 쉽게 재사용 하도록 도와줌
이미 쓰고 있었다.
mocker...

이번에는 fixture를 만들어 보자...

우리는 앞에서 클라이언트를 만들어서 반복적으로 쓰고 있었다.
```python

client = TestClient(app=app)
```

파일마다 객체를 생성하지 않고 미리 픽스처로 등록을 하고 재사용해보자.

tests 패키지 안에 conftest.py를 만들고 정의해주자.
```python

import pytest
from fastapi.testclient import TestClient
from main import app

# fixture는 함수형태로 만들어야함
@pytest.fixture
def client():
    return TestClient(app=app)

```
위와 같이하면 pytest가 이 함수를 fixture로 인식을 해서 테스트 코드 안에서 글로벌하게 사용할수 있게 된다.

이제 test_main.py에서 client를 지우고 코드를 수정하자.

```python
#client = TestClient(app=app) # 사용 x

def test_health_check(client):
    response = client.get("/") #
    
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


def test_get_todos(client, mocker):

    mocker.patch(...
```

## 44. GET 단일 조회 API 테스트 코드
200, 오류 둘다 테스트 하도록 테스트 코드를 작성하자.

```python
def test_get_todo(client, mocker):
    # 200
    mocker.patch(
        "main.get_todo_by_todo_id", 
        return_value = ToDo(id=1, contents="todo", is_done=True))
    
    response = client.get("/todos/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "todo", "is_done": True}
    
    # 400
    mocker.patch(
        "main.get_todo_by_todo_id", 
        return_value = None)
    
    response = client.get("/todos/1")
    assert response.status_code == 404
    assert response.json() == {"detail": "ToDo Not Found"}  
```

테스트함수 개별로 실행하는 방법도 있다.
```bash
pytest tests/test_main.py::함수이름

# 예시
pytest tests/test_main.py::test_get_todo
```

## 45. POST API 테스트 코드

spy에 대해서 다시 볼걸

```python
def test_create_todo(client, mocker):
    create_spy = mocker.spy(ToDo, "create")
    mocker.patch(
        "main.create_todo", 
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
```


### 46 Patch api 테스트 코드
다시 볼것것
```python
def test_update_todo(client, mocker):
    # 200
    mocker.patch(
        "main.get_todo_by_todo_id", 
        return_value = ToDo(id=1, contents="todo", is_done=True))
    
    undone = mocker.patch.object(ToDo, "undone")
    
    mocker.patch(
        "main.update_todo", 
        return_value = ToDo(id=1, contents="todo", is_done=False))
    
    response = client.patch("/todos/1", json={"is_done": False})
    
    undone.assert_called_once_with()
    assert response.status_code == 200
    assert response.json() == {"id": 1, "contents": "todo", "is_done": False}
    
    # 404
    mocker.patch(
        "main.get_todo_by_todo_id", 
        return_value = None)
    
    response = client.patch("/todos/1", json = {"is_done": True})
    assert response.status_code == 404
    assert response.json() == {"detail": "ToDo Not Found"}     
```