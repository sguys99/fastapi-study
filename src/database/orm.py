from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

from schema.request import CreateToDoRequest

Base = declarative_base() # 배이스 클래스 생성

class ToDo(Base): # mysql에서 생성한 동일한 테이블 구조
    __tablename__ = "todo"
    
    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(256), nullable=False)
    is_done = Column(Boolean, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id")) # 외래 키 추가
    
    def __repr__(self): # 내부 정보 출력, 확인위해
        return f"ToDo(id={self.id}, contents={self.contents}, is_done={self.is_done})"
    
    @classmethod
    def create(cls, request: CreateToDoRequest)-> "ToDo":
        return cls( # id는 DB에서 별도(자동) 지정되도록 했기 때문에, 두개만 지정하면됨
            contents=request.contents,
            is_done=request.is_done
        )
        
    def done(self) -> "ToDo":
        self.is_done = True
        return self
    
    def undone(self) -> "ToDo":
        self.is_done = False
        return self
    

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