from typing import Optional, Dict, Optional

from .constants import REQUEST_TYPES, POWER_STATES


class AsyncdactylBaseError(Exception):
    pass

class ClientConfigError(AsyncdactylBaseError):
    def __init__(self, message: Optional[str] = "An error occured with the configuration of the client.") -> None:
        super().__init__(message)

class BadRequestType(AsyncdactylBaseError):
    def __init__(self, method: str) -> None:
        super().__init__(f"Invalid request type '{method}'."
            f"Must be {', '.join(REQUEST_TYPES[:-1])} or {REQUEST_TYPES[-1]}")
        
class BadPowerState(AsyncdactylBaseError):
    def __init__(self, state: str) -> None:
        super().__init__(f"Invalid power state '{state}'."
            f"Must be {', '.join(POWER_STATES[:-1])} or {POWER_STATES[-1]}")

class BadRequestError(AsyncdactylBaseError):  # 400
    def __init__(self, error: Optional[Dict[str, Dict]]) -> None:
        self.error = error
        try:
            message = f"{error['code']} (status={error['status']}): {error['detail']}"
        except (ValueError, KeyError):
            error = None
        super().__init__(message or "An error occured with the request.")

class RateLimitExceeded(AsyncdactylBaseError):  # 429
    def __init__(self, message: Optional[str] = "The rate limit has been exceeded.") -> None:
        super().__init__(message)
        
class OperationFailed(AsyncdactylBaseError):
    def __init__(self, excpeted_response: int, received_response: int) -> None:
        super().__init__("The requested action was not completed"
            " (the status does not match that on the api documentation):"
            f" {excpeted_response} (response expected) != {received_response} (response received)."
            f"\nExplaination on this code: https://developer.mozilla.org/en/docs/Web/HTTP/Status/{received_response}")

class NotFound(AsyncdactylBaseError):
    def __init__(self, message: Optional[str] = None):
        if not message:
            message = "How? Where!? I can't find it! - The resource could not be found on the server."
        super().__init__(message)