"""
Global Exception Handler
========================
Centralized error handling for consistent API responses.

Why This Matters:
- Prevents internal stack traces from leaking to clients
- Ensures consistent error response format across all endpoints
- Makes debugging easier with structured error information
- Improves security by hiding implementation details

Error Response Format:
{
    "error": {
        "code": "TRADE_NOT_FOUND",
        "message": "Trade with ID 123 not found",
        "details": null  // Optional additional context
    }
}
"""

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

# Configure logging for error tracking
logger = logging.getLogger(__name__)


class AppException(Exception):
    """
    Base exception class for application-specific errors.
    
    Extend this class to create domain-specific exceptions
    that include error codes and appropriate HTTP status codes.
    """
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: dict = None
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        super().__init__(message)


class TradeNotFoundError(AppException):
    """Raised when a requested trade doesn't exist or doesn't belong to user."""
    def __init__(self, trade_id: int):
        super().__init__(
            status_code=404,
            code="TRADE_NOT_FOUND",
            message=f"Trade with ID {trade_id} not found",
            details={"trade_id": trade_id}
        )


class TradeAlreadyClosedError(AppException):
    """Raised when attempting to close an already-closed trade."""
    def __init__(self, trade_id: int):
        super().__init__(
            status_code=400,
            code="TRADE_ALREADY_CLOSED",
            message=f"Trade {trade_id} is already closed",
            details={"trade_id": trade_id}
        )


class InvalidCredentialsError(AppException):
    """Raised when login credentials are incorrect."""
    def __init__(self):
        super().__init__(
            status_code=401,
            code="INVALID_CREDENTIALS",
            message="Invalid username or password"
        )


class UsernameExistsError(AppException):
    """Raised when attempting to register with an existing username."""
    def __init__(self, username: str):
        super().__init__(
            status_code=409,
            code="USERNAME_EXISTS",
            message=f"Username '{username}' is already taken"
        )


def create_error_response(
    status_code: int,
    code: str,
    message: str,
    details: dict = None
) -> JSONResponse:
    """
    Create a standardized error response.
    
    This ensures all error responses follow the same structure,
    making it easier for frontend developers to handle errors.
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": details
            }
        }
    )


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """
    Handle custom application exceptions.
    
    Logs the error and returns a structured response.
    """
    logger.warning(f"Application error: {exc.code} - {exc.message}")
    return create_error_response(
        exc.status_code,
        exc.code,
        exc.message,
        exc.details
    )


async def http_exception_handler(
    request: Request, 
    exc: StarletteHTTPException
) -> JSONResponse:
    """
    Handle standard HTTP exceptions.
    
    Converts FastAPI's HTTPException to our standard format.
    """
    # Map common status codes to error codes
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        422: "VALIDATION_ERROR",
        500: "INTERNAL_ERROR"
    }
    
    code = code_map.get(exc.status_code, "HTTP_ERROR")
    
    return create_error_response(
        exc.status_code,
        code,
        str(exc.detail)
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    Handle Pydantic validation errors.
    
    Converts validation errors to a user-friendly format.
    This is particularly useful for trading applications where
    users need clear feedback on invalid price/quantity inputs.
    """
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"]
        })
    
    logger.info(f"Validation error: {errors}")
    
    return create_error_response(
        status_code=422,
        code="VALIDATION_ERROR",
        message="Request validation failed",
        details={"errors": errors}
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for unexpected exceptions.
    
    IMPORTANT: In production, this prevents stack traces from
    being exposed to clients. The error is logged internally
    for debugging, but users only see a generic message.
    """
    # Log the full exception for debugging
    logger.exception(f"Unhandled exception: {exc}")
    
    return create_error_response(
        status_code=500,
        code="INTERNAL_ERROR",
        message="An unexpected error occurred. Please try again later."
    )
