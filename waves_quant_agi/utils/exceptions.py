### utils/exceptions.py

class BaseAppException(Exception):
    """Base exception class for the application."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class AuthenticationError(BaseAppException):
    """Raised when authentication fails."""
    pass

class AuthorizationError(BaseAppException):
    """Raised when a user is not authorized to perform an action."""
    pass

class NotFoundError(BaseAppException):
    """Raised when a requested resource is not found."""
    pass

class ValidationError(BaseAppException):
    """Raised when data validation fails."""
    pass

class InsufficientFundsError(BaseAppException):
    """Raised when a withdrawal or trade fails due to lack of funds."""
    pass

class StrategyError(BaseAppException):
    """Raised when there is an error related to a trading strategy."""
    pass

class PaymentProcessingError(BaseAppException):
    """Raised when a payment fails or cannot be verified."""
    pass
