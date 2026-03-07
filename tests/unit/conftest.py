from typing import Callable
from uuid import uuid4

import pytest
from faker import Faker

from app.domain import User

fake = Faker()
Faker.seed(23)

type UserFactory = Callable[..., list[User]]


@pytest.fixture()
def make_users() -> Callable[..., list[User]]:
    def _make_users(user_count: int) -> list[User]:
        return [
            User(
                id=uuid4(),
                firstname=fake.first_name(),
                lastname=fake.last_name(),
                email=fake.email(),
                password_hash=fake.password().encode(),
                salt=fake.password(),
            )
            for _ in range(user_count)
        ]

    return _make_users
