from fastapi import APIRouter

router = APIRouter(prefix="/users")

@router.post("/sign-up", status_code=201)
def user_sign_up_handler():
    # 1. request body로 username, password 받기
    # 2. password -> hassing -> hassed_password
    # 4. user -> db insert
    # 5. return user(id, username) # pw는 알려주면 안되기 때문에
    return True