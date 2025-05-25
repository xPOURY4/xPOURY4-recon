"""
Custom exceptions for xPOURY4 Recon
Author: xPOURY4
"""


class ReconException(Exception):
    """Base exception for all reconnaissance operations"""
    pass


class APIException(ReconException):
    """Exception raised when API calls fail"""
    def __init__(self, message: str, status_code: int = None, api_name: str = None):
        self.status_code = status_code
        self.api_name = api_name
        super().__init__(message)


class ValidationException(ReconException):
    """Exception raised when input validation fails"""
    pass


class ConfigurationException(ReconException):
    """Exception raised when configuration is invalid"""
    pass


class NetworkException(ReconException):
    """Exception raised when network operations fail"""
    pass 