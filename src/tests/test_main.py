from fastapi.testclient import TestClient

from database.orm import ToDo
from main import app



#client = TestClient(app=app) # 우리가 만든 app이 테스트 클라이언트가 되서 테스트를 진행하는 방식

def test_health_check(client):
    response = client.get("/") # 이방식으로 앱에 get요청, 결과를 response에 저장
    
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
    
    
# def test_get_todos():
#     # 정상순서 검증
#     response = client.get("/todos") 
    
#     assert response.status_code == 200
#     assert response.json() == {
#         "todos": [
#             {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
#             {"id": 2, "contents": "FastAPI Section 1", "is_done": True},
#             {"id": 3, "contents": "FastAPI Section 2", "is_done": True},
#         ]
#     }    

#     # 역순 검증 order=DESC
#     response = client.get("/todos?order=DESC") 
    
#     assert response.status_code == 200
#     assert response.json() == {
#         "todos": [
#             {"id": 3, "contents": "FastAPI Section 2", "is_done": True},
#             {"id": 2, "contents": "FastAPI Section 1", "is_done": True},
#             {"id": 1, "contents": "FastAPI Section 0", "is_done": True},
#         ]
#     }        

# mocking 반영
def test_get_todos(client, mocker):
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
    