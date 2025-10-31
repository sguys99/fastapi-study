from fastapi.testclient import TestClient

from main import app


client = TestClient(app=app) # 우리가 만든 app이 테스트 클라이언트가 되서 테스트를 진행하는 방식

def test_health_check():
    response = client.get("/") # 이방식으로 앱에 get요청, 결과를 response에 저장
    
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}
    
    
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