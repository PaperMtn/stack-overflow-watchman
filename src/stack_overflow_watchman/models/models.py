from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass(frozen=True, slots=True)
class Owner:
    account_id: int
    reputation: int
    user_id: int
    user_type: str
    profile_image: str
    display_name: str
    link: str


@dataclass(frozen=True, slots=True)
class Question:
    tags: List[str]
    owner: Owner
    is_answered: bool
    view_count: int
    answer_count: int
    score: int
    last_activity_date: int
    creation_date: int
    question_id: int
    link: str
    title: str
    last_edit_date: Optional[int] = None
    accepted_answer_id: Optional[int] = None
    bounty_amount: Optional[int] = None
    bounty_closes_date: Optional[int] = None
    closed_date: Optional[int] = None
    closed_reason: Optional[str] = None
    collectives: Optional[List[str]] = None
    community_owned_date: Optional[int] = None
    content_license: Optional[str] = None
    locked_date: Optional[int] = None
    migrated_from: Optional[Dict] = None
    migrated_to: Optional[Dict] = None
    posted_by_collectives: Optional[List[str]] = None
    protected_date: Optional[int] = None


@dataclass(frozen=True, slots=True)
class Answer:
    owner: Owner
    is_accepted: bool
    score: int
    last_activity_date: int
    creation_date: int
    answer_id: int
    question_id: int
    last_edit_date: Optional[int] = None
    collectives: Optional[List[str]] = None
    community_owned_date: Optional[int] = None
    content_license: Optional[str] = None
    locked_date: Optional[int] = None
    posted_by_collectives: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    link: Optional[str] = None
    body: Optional[str] = None


@dataclass(frozen=True, slots=True)
class User:
    badge_counts: Dict[str, int]
    account_id: int
    is_employee: bool
    last_access_date: int
    reputation_change_year: int
    reputation_change_quarter: int
    reputation_change_month: int
    reputation_change_week: int
    reputation_change_day: int
    reputation: int
    creation_date: int
    user_type: str
    user_id: int
    link: str
    profile_image: str
    display_name: str
