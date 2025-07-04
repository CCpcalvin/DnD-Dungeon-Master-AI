import enum


class RollResult(str, enum.Enum):
    CRITICAL_SUCCESS = "Critical Success"
    SUCCESS = "Success"
    FAILURE = "Failure"
    CRITICAL_FAILURE = "Critical Failure"
