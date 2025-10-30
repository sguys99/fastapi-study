from fastapi.testclient import TestClient

from main import app


client = TestClient(app=app) # 우리가 만든 app이 테스트 클라이언트가 되서 테스트를 진행하는 방식

def test_health_check():
    response = client.get("/") # 이방식으로 앱에 get요청, 결과를 response에 저장
    
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}