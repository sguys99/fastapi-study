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


