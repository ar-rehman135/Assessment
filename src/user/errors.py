from src.core.exceptions import RequestException


class UserErrors:
    EMAIL_OR_PASSWORD_INCORRECT = RequestException(
        "EMAIL_OR_PASSWORD_INCORRECT",
        "The requested email or password is incorrect!",
        404,
    )
    USER_NOT_FOUND = RequestException(
        "USER_NOT_FOUND",
        "The requested user was not found",
        404,
    )
    EMAIL_ALREADY_EXISTS = RequestException(
        "EMAIL_ALREADY_EXISTS",
        "This email is already registered",
        400,
    )
    USER_UPDATE_ERROR = RequestException(
        "USER_UPDATE_ERROR",
        "An error occurred during user update",
        400,
    )

    @staticmethod
    def dynamic_error(
        code: str, message: str, status_code: int = 400
    ) -> RequestException:
        """
        Create a dynamic RequestException with the given code, message, and status code.
        :param code: The error code.
        :param message: The error message.
        :param status_code: The HTTP status code (default is 400).
        :return: A new instance of RequestException.
        """
        return RequestException(code, message, status_code)
