from uuid import UUID, uuid4

import pytest
from joserfc import jwt

from app.domain.ports import UserRepository
from app.domain.users import User
from app.service import UserService


class InMemoryUserRepository(UserRepository):

    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def get(self, id: UUID) -> User:
        return self._users[id]

    async def save(self, user: User) -> UUID:
        id = uuid4()
        user.id = id
        self._users[id] = user
        return id

    async def list(self) -> list[User]:
        return list(self._users.values())


class TestUserService:

    @pytest.mark.asyncio
    async def test_create_user(self) -> None:
        repository = InMemoryUserRepository()
        service = UserService(repository)
        assert service.users == []

        await service.create_user("John", "Doe", "johndoe@test.com", "test")
        assert len(service.users) == 1
        assert service.users[0].firstname == "John"
        assert service.users[0].lastname == "Doe"
        assert service.users[0].password_hash != "test".encode()

    @pytest.mark.asyncio
    async def test_encode_token(self) -> None:
        # https://datatracker.ietf.org/doc/html/rfc7519
        repository = InMemoryUserRepository()
        service = UserService(repository)
        jwt_claims_set = {"id": 1, "name": "toto", "iss": "international space station"}
        token = await service.encode_jwt_token(jwt_claims_set)
        assert token
        assert len(token.split(".")) == 3

        decoded_token: jwt.Token = jwt.decode(token, service.secret_key)
        assert decoded_token.claims == jwt_claims_set
        assert decoded_token.header["alg"] == service.encoding_algorithm

    @pytest.mark.asyncio
    async def test_authenticate_user(self) -> None:
        repository = InMemoryUserRepository()
        service = UserService(repository)
        await service.create_user("John", "Doe", "johndoe@test.com", "test")
        bearer_token: str = await service.authenticate_user("johndoe@test.com", "test")
        assert bearer_token
