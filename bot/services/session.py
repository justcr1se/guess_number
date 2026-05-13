import time
from dataclasses import dataclass
from typing import Optional

from bot.config import SESSION_TTL_SECONDS


@dataclass
class UserSession:
    last_analysis: str
    questions_block: str
    updated_at: float


class SessionStore:
    def __init__(self, ttl_seconds: int = SESSION_TTL_SECONDS) -> None:
        self._sessions: dict[int, UserSession] = {}
        self._ttl = ttl_seconds

    def set(self, user_id: int, last_analysis: str, questions_block: str = "") -> None:
        self._sessions[user_id] = UserSession(
            last_analysis=last_analysis,
            questions_block=questions_block,
            updated_at=time.time(),
        )

    def get(self, user_id: int) -> Optional[UserSession]:
        session = self._sessions.get(user_id)
        if session is None:
            return None
        if time.time() - session.updated_at > self._ttl:
            self._sessions.pop(user_id, None)
            return None
        return session

    def clear(self, user_id: int) -> None:
        self._sessions.pop(user_id, None)


session_store = SessionStore()
