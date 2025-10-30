# 데이터를 조회하는 함수를 여기에 정의

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.orm import ToDo
from typing import List

# ToDo를 리스트에 담아서 리턴
def get_todos(session: Session) -> List[ToDo]:
    return list(session.scalars(select(ToDo)))


# 개별 조회, 조회 항목이 없으면 None을 리턴
def get_todo_by_todo_id(session: Session, todo_id: int) -> ToDo | None:
    return session.scalar(select(ToDo).where(ToDo.id == todo_id))


def create_todo(session: Session, todo: ToDo) -> ToDo:
    session.add(instance=todo)
    session.commit() # db에저장
    session.refresh(instance=todo) # 데이터를 다시 읽어주는 부분(db read), 이때 todo_id 값이 반영되서 저장됨
    return todo # id가 포함된 todo를 리턴


# 사실 create_todo와 동일
def update_todo(session: Session, todo: ToDo) -> ToDo:
    session.add(instance=todo)
    session.commit() 
    session.refresh(instance=todo) 
    return todo 