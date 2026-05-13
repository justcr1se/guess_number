import time
from dataclasses import dataclass, field
from typing import Optional

from bot.config import SESSION_TTL_SECONDS

MAX_ANALYSES_PER_SESSION = 5


@dataclass
class StoredAnalysis:
    text: str
    questions_block: str
    created_at: float


@dataclass
class UserSession:
    analyses: list[StoredAnalysis] = field(default_factory=list)
    profile: str = ""
    updated_at: float = field(default_factory=time.time)

    @property
    def last_analysis(self) -> Optional[StoredAnalysis]:
        return self.analyses[-1] if self.analyses else None

    @property
    def last_questions_block(self) -> str:
        last = self.last_analysis
        return last.questions_block if last else ""


class SessionStore:
    def __init__(self, ttl_seconds: int = SESSION_TTL_SECONDS) -> None:
        self._sessions: dict[int, UserSession] = {}
        self._ttl = ttl_seconds

    def _touch(self, session: UserSession) -> None:
        session.updated_at = time.time()

    def _get_fresh(self, user_id: int) -> Optional[UserSession]:
        session = self._sessions.get(user_id)
        if session is None:
            return None
        if time.time() - session.updated_at > self._ttl:
            self._sessions.pop(user_id, None)
            return None
        return session

    def add_analysis(self, user_id: int, text: str, questions_block: str = "") -> None:
        session = self._sessions.get(user_id)
        if session is None or time.time() - session.updated_at > self._ttl:
            session = UserSession()
            self._sessions[user_id] = session
        session.analyses.append(
            StoredAnalysis(text=text, questions_block=questions_block, created_at=time.time())
        )
        if len(session.analyses) > MAX_ANALYSES_PER_SESSION:
            session.analyses = session.analyses[-MAX_ANALYSES_PER_SESSION:]
        self._touch(session)

    def set_profile(self, user_id: int, profile: str) -> None:
        session = self._sessions.get(user_id)
        if session is None:
            session = UserSession()
            self._sessions[user_id] = session
        session.profile = profile
        self._touch(session)

    def get(self, user_id: int) -> Optional[UserSession]:
        return self._get_fresh(user_id)

    def clear_analyses(self, user_id: int) -> None:
        session = self._get_fresh(user_id)
        if session is None:
            return
        session.analyses.clear()
        self._touch(session)

    def clear(self, user_id: int) -> None:
        self._sessions.pop(user_id, None)


session_store = SessionStore()
