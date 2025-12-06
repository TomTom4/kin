class BaseError(Exception):
    MSG = "This is application base exception"

    def __init__(self, message: str | None = None) -> None:
        self.message = message or self.MSG


class AppointmentError(BaseError):
    MSG = "The appointment is invalid"


class InvalidDateAndTimeError(AppointmentError):
    MSG = "Date and Time invalid: you need to set up an appointment somewhere from now and the future."


class OverlappingAppointmentError(AppointmentError):
    MSG = "Invalid appointment: the appointment demands provided overlap."


class UserDontExistsError(BaseError):
    MSG = "The given email adress is unknown to us"


class WrongPasswordError(BaseError):
    MSG = "The given password is wrong"
