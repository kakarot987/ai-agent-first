class AIAgentException(Exception):
    """Base exception for AI Agent."""

    pass


class APIException(AIAgentException):
    """Exception raised for API-related errors."""

    pass


class ConfigurationException(AIAgentException):
    """Exception raised for configuration errors."""

    pass


class ValidationException(AIAgentException):
    """Exception raised for validation errors."""

    pass
