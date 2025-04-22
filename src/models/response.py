from dataclasses import dataclass


@dataclass
class Response:
    id: int
    job_id: int
    message: str
    user_id: int