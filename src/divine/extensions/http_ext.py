from typing import Any

from pydantic import (
    BaseModel,
    Field,
    PositiveInt,
)


class HttpProblemBase(BaseModel):
    """Model representing a RFC9457 problem.

    https://datatracker.ietf.org/doc/html/rfc9457
    """

    status: PositiveInt = Field(description="The HTTP status code, usually same as headers")

    title: str = Field(
        min_length=1,
        description="A short, human-readable summary of the problem type."
        " It does not change from occurrence to occurrence of the problem.",
    )
    detail: str = Field(
        default="",
        description="A human-readable explanation specific to this occurrence of the problem.",
    )
    type: str = Field(
        default="about:blank",
        description="""
        A URI reference that identifies the problem type.
        This specification should provide a human-readable documentation for the problem type.
        When this member is not present, its value is assumed to be "about:blank".
        """,
    )
    instance: str = Field(
        default="",
        description="A URI reference that identifies the specific occurrence of the problem.",
    )
    error_code: str = Field(description="A the generic identifier of the error, to group errors.")
    metadata: dict[str, Any] | None = Field(
        default=None,
        description="Extension to the RFC9457. Should be used to provide any extra information to the caller.",
    )
