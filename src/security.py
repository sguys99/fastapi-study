from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import Depends, HTTPException


# api에서 dependency로 사용할 수 있는 함수 정의

def get_access_token(
    auth_header: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> str:
    if auth_header is None:
        raise HTTPException(
            status_code=401,
            detail="Not Authorized"
            )
    return auth_header.credentials