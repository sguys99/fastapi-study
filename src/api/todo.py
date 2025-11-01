
from fastapi import Depends, FastAPI, Body, HTTPException, APIRouter
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database.connection import get_db
from database.repository import delete_todo, get_todo_by_todo_id, get_todos, create_todo, update_todo, delete_todo


from database.orm import ToDo
from typing import List

from schema.request import CreateToDoRequest
from schema.response import ToDoListSchema, ToDoSchema
# from main import app


router = APIRouter(prefix="/todos")


@router.get("", status_code=200)
def get_todos_handler(
    order: str| None = None,
    session: Session = Depends(get_db)
    ) -> ToDoListSchema:
    # result = list(todo_data.values())
    
    todos: List[ToDo] = get_todos(session=session)
    if order and order == "DESC": # DB에서 역정렬 해야지면, 일단 이렇게
        return ToDoListSchema(
        todos = [ToDoSchema.model_validate(todo) for todo in todos[::-1]]
    )

    return ToDoListSchema(
        todos = [ToDoSchema.model_validate(todo) for todo in todos]
    )


# 단일 todo를 조회하는 api
@router.get("/{todo_id}", status_code=200)
def get_todo_handler(
    todo_id: int,
    session: Session = Depends(get_db)
    ) -> ToDoSchema:
    # todo = todo_data.get(todo_id)
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)
    if todo:
        # return todo
        return ToDoSchema.model_validate(todo)
    raise HTTPException(status_code=404, detail="ToDo Not Found")

    
# post 메서드를 사용하여 매핑
# pydantic을 사용하여 request body 생성 가능

@router.post("", status_code=201)
def create_todo_handler(
    request: CreateToDoRequest,
    session: Session = Depends(get_db)
    ) -> ToDoSchema:
    #todo_data[request.id] = request.model_dump()
    todo: ToDo = ToDo.create(request=request) # id = None
    todo: ToDo = create_todo(session=session, todo=todo) #id=int
    # return todo_data[request.id]
    return ToDoSchema.model_validate(todo)


@router.patch("/{todo_id}", status_code=200)
def update_todo_handler(
    todo_id: int,
    is_done: bool = Body(..., embed=True),
    session: Session = Depends(get_db)
    ):
    
    # todo = todo_data.get(todo_id)
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)
    if todo: #update
        todo.done() if is_done else todo.undone()
        todo: ToDo = update_todo(session=session, todo=todo)
        return ToDoSchema.model_validate(todo) 
    raise HTTPException(status_code=404, detail="ToDo Not Found")


# delete
@router.delete("/{todo_id}", status_code=204)
def delete_todo_handler(
    todo_id: int,
    session: Session = Depends(get_db)
    ):
    todo: ToDo | None = get_todo_by_todo_id(session=session, todo_id=todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="ToDo Not Found")
    
    # delete
    delete_todo(session=session, todo_id=todo_id)
