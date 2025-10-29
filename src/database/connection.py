from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "mysql+pymysql://root:todos@127.0.0.1:3306/todos"


# sqlalchemy로 db 접속을위해서는 먼저 엔진이라는 객체를 생성해야함
engine = create_engine(DATABASE_URL, echo=True) # echo: 쿼리 사용시점에 쿼리 프린트


SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# commit, flush를 명시적으로 진행하겠다는 의미

# README.md의 테스트 코드 실행할 것