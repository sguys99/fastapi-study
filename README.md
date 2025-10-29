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