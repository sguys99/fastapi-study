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