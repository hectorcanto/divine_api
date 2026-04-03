import http
from typing import (
    Generic,
    TypeVar,
)

from fastapi.requests import Request
from fastapi.responses import JSONResponse
from pydantic import (
    Field,
    PositiveInt,
)

from divine.extensions.http_ext import HttpProblemBase


class AuthenticationError(HttpProblemBase):
    title: str = Field(
        default="Authentication error",
        min_length=1,
        description="A short, human-readable summary of the problem type."
        " It does not change from occurrence to occurrence of the problem.",
    )
    status: PositiveInt = Field(default=http.HTTPStatus.UNAUTHORIZED)
    error_code: str = Field(default="AuthError")
    # TODO(h): group error_codes


class UserNotFoundProblem(HttpProblemBase):
    title: str = Field(
        default="User not found",
        min_length=1,
        description="A short, human-readable summary of the problem type."
        " It does not change from occurrence to occurrence of the problem.",
    )
    status: PositiveInt = Field(default=http.HTTPStatus.NOT_FOUND)
    error_code: str = Field(default="UserNotFound")


class DeviceNotFoundProblem(HttpProblemBase):
    title: str = Field(
        default="Session not found",
        min_length=1,
        description="A short, human-readable summary of the problem type."
        " It does not change from occurrence to occurrence of the problem.",
    )
    status: PositiveInt = Field(default=http.HTTPStatus.NOT_FOUND)
    error_code: str = Field(default="SessionNotFound")


PR = TypeVar("PR", bound=HttpProblemBase)


class ProblemJsonResponse(JSONResponse, Generic[PR]):
    media_type: str = "application/problem+json"

    def __init__(self, problem: HttpProblemBase, request: Request):
        super().__init__(
            content=problem.model_dump(exclude_none=True),
            status_code=problem.status,
            media_type=self.media_type,
            headers={
                "Content-Language": "en",
                "X-Error-Code": problem.error_code,
            },
        )
        self.problem = problem
