from hashlib import sha3_512
from secrets import choice
from string import ascii_letters, digits

from pydantic import EmailStr

from .base_model import KinModel


class User(KinModel):
    firstname: str
    lastname: str
    email: EmailStr
    password_hash: bytes
    salt: str

    @staticmethod
    async def generate_salt() -> str:
        alphabet = ascii_letters + digits
        return "".join([choice(alphabet) for _ in range(32)])

    @staticmethod
    async def hash_password(salted_password: str) -> bytes:
        hashed_salted_password: bytes = sha3_512(salted_password.encode()).digest()
        return hashed_salted_password
