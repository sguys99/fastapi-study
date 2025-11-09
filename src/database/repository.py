# 데이터를 조회하는 함수를 여기에 정의

from sqlalchemy import select, delete
from sqlalchemy.orm import Session

from database.orm import ToDo
from typing import List
from fastapi import Depends
from database.connection import get_db
from database.orm import User

class ToDoRepository:
    def __init__(self, session: Session = Depends(get_db)): # dependency injection 추가가
        self.session = session

    def get_todos(self) -> List[ToDo]:
        return list(self.session.scalars(select(ToDo)))

    def get_todo_by_todo_id(self, todo_id: int) -> ToDo | None:
        return self.session.scalar(select(ToDo).where(ToDo.id == todo_id))

    def create_todo(self, todo: ToDo) -> ToDo:
        self.session.add(instance=todo)
        self.session.commit() # db에저장
        self.session.refresh(instance=todo) # 데이터를 다시 읽어주는 부분(db read), 이때 todo_id 값이 반영되서 저장됨
        return todo # id가 포함된 todo를 리턴

    def update_todo(self, todo: ToDo) -> ToDo:
        self.session.add(instance=todo)
        self.session.commit() 
        self.session.refresh(instance=todo) 
        return todo 

    def delete_todo(self, todo_id: int) -> None:
        self.session.execute(delete(ToDo).where(ToDo.id == todo_id))
        self.session.commit()
        

class UserRepository:
    def __init__(self, session: Session = Depends(get_db)):
        self.session = session
        
    def get_user_by_username(self, username: str) -> User | None:
        return self.session.scalar(
            select(User).where(User.username == username)
            )

    def save_user(self, user: User) -> User:
        self.session.add(instance=user)
        self.session.commit()
        self.session.refresh(instance=user)
        return user