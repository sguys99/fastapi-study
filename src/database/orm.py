from sqlalchemy import Boolean, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base() # 배이스 클래스 생성

class ToDo(Base): # mysql에서 생성한 동일한 테이블 구조
    __tablename__ = "todo"
    
    id = Column(Integer, primary_key=True, index=True)
    contents = Column(String(256), nullable=False)
    is_done = Column(Boolean, nullable=False)
    
    def __repr__(self): # 내부 정보 출력, 확인위해
        return f"ToDo(id={self.id}, contents={self.contents}, is_done={self.is_done})"
    
    
