from abc import ABC, abstractmethod
from uuid import UUID

from .appointments import Appointment
from .users import User


class UserRepository(ABC):

    @abstractmethod
    async def get(self, id: UUID) -> User:
        raise NotImplementedError

    @abstractmethod
    async def save(self, user: User) -> UUID:
        raise NotImplementedError

    @abstractmethod
    async def list(self) -> list[User]:
        raise NotImplementedError


class AppointmentRepository(ABC):

    @abstractmethod
    async def get(self, id: UUID) -> Appointment:
        raise NotImplementedError

    @abstractmethod
    async def save(self, user: Appointment) -> UUID:
        raise NotImplementedError

    @abstractmethod
    async def list(self) -> list[Appointment]:
        raise NotImplementedError
