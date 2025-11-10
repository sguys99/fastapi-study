from fastapi import APIRouter, Depends, HTTPException
from schema.request import SignUpRequest
from service.user import UserService
from database.orm import User
from database.repository import UserRepository
from schema.response import UserSchema
from schema.request import LogInRequest
from schema.response import JWTResponse
from schema.request import CreateOTPRequest
from security import get_access_token
from cache import redis_client

router = APIRouter(prefix="/users")

@router.post("/sign-up", status_code=201)
def user_sign_up_handler(
    request: SignUpRequest,
    user_service: UserService = Depends(),
    user_repo: UserRepository = Depends(),
    ):
    # 1. request body로 username, password 받기
    # 2. password -> hassing -> hassed_password
    hashed_password: str = user_service.hash_password(
        plain_password=request.password
        )
    
    # 3. User(usernam, hashed_password)
    user: User = User.create(
        username=request.username,
        hashed_password=hashed_password
    ) # 이시점에는 user의 id가 None이다. orm 객체로만 있는 상태
    
    # 4. user -> db insert
    user: User = user_repo.save_user(user=user) # 이시점에는 user의 id가 int이다. orm 객체가 db에 저장되고 다시 읽어와서 반영된 상태
    
    
    # 5. return user(id, username) # pw는 알려주면 안되기 때문에
    return UserSchema.model_validate(user)


@router.post("/log-in")
def user_log_in_handler(
    request: LogInRequest,
    user_service: UserService = Depends(),
    user_repo: UserRepository = Depends(),
    ):
    # 1. request body로 username, password 받기
    # 2. DB에서 유저 정보 읽어오기
    user: User | None = user_repo.get_user_by_username(
        username=request.username
        )
    if not user:
        raise HTTPException(
            status_code=404, 
            detail="User Not Found"
            )
    
    # 3. username, password 검증(bcrypt.checkpw)
    verified: bool = user_service.verify_password(
        plain_password=request.password,
        hashed_password=user.password
    )
    if not verified:
        raise HTTPException(
            status_code=401,
            detail="Not Authorized"
            )
    
    # 4. jwt 생성
    access_token: str = user_service.create_jwt(
        username=user.username
    )
    # 5. jwt 반환
    return JWTResponse(access_token=access_token)


@router.post("/email/otp")
def create_otp_handler(
    request: CreateOTPRequest, 
    _: str = Depends(get_access_token), # 인증된 사용자 확인, 검증만 하고 사용하지 않으므로로
    user_service: UserService = Depends(),
):
    # 1. access_token 파라미터 받기: 로그인 된 사용자인지 확인
    # 2. request body로 email 정보 받기
    # 3. otp 생성 (랜덤 값 4자리)
    otp: int = user_service.create_otp()
    
    # 4. email, otp를 key, value로 redis에 저장 (3분 만료)
    redis_client.set(name=request.email, value=otp)
    redis_client.expire(name=request.email, time=3*60) # 3분 만료
    
    # 5. otp를 email로 전송???
    
    return {"otp": otp}


@router.post("/email/otp/verify")
def verify_otp_handler():
    return True