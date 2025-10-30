# 데이터를 조회하는 함수를 여기에 정의

from sqlalchemy import select
from sqlalchemy.orm import Session

from database.orm import ToDo
from typing import List

# ToDo를 리스트에 담아서 리턴
def get_todos(session: Session) -> List[ToDo]:
    return list(session.scalars(select(ToDo)))
