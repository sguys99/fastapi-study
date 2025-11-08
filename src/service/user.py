import bcrypt

class UserService:
    encoding: str = "UTF-8"
    
    def hash_password(self, plain_password: str) -> str:
        hash_password: bytes = bcrypt.hashpw(
            plain_password.encode(self.encoding), 
            salt=bcrypt.gensalt(),
            )
        return hash_password.decode(self.encoding)
