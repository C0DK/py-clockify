"""
The data classes for the objects
returned by API.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
from enum import Enum, auto


class CannotDecodeException(Exception):
    pass


def _estimate_to_timedelta(estimate: str) -> timedelta:
    """
    Coinify uses a weird ass syntax for timedelta.
    Example: PT1H30M15S - 1 hour 30 minutes 15 seconds
    This function converts such a string to a timedelta
    :param estimate: the estimate from coinify
    :return: a timedelta
    """
    estimate = estimate.split("PT")[1]
    h, estimate = estimate.split("H") if "H" in estimate else (0, estimate)
    m, estimate = estimate.split("M") if "M" in estimate else (0, estimate)
    s = estimate.split("S")[0] if "S" in estimate else 0
    h = int(h)
    m = int(m)
    s = int(s)
    return timedelta(hours=h, minutes=m, seconds=s)


@dataclass
class HourlyRate:
    currency: str
    amount: Decimal

    def __init__(self, data: Dict[str, Any]):
        self.currency = data["currency"]
        self.amount = Decimal(data["amount"])


@dataclass
class Tag:
    uid: str
    name: str
    workspace_id: str

    def __init__(self, data: Dict[str, Any]):
        self.uid = data["id"]
        self.name = data["name"]
        self.workspace_id = data["workspaceId"]


class MembershipStatus(Enum):
    PENDING = auto()
    ACTIVE = auto()
    DECLINED = auto()
    INACTIVE = auto()

    @staticmethod
    def from_json(data: str) -> "MembershipStatus":
        if data == "PENDING":
            return MembershipStatus.PENDING
        if data == "ACTIVE":
            return MembershipStatus.ACTIVE
        if data == "DECLINED":
            return MembershipStatus.DECLINED
        if data == "INACTIVE":
            return MembershipStatus.INACTIVE

        raise CannotDecodeException(data)


@dataclass
class Membership:
    user_id: str
    target_id: str
    hourly_rate: Optional[HourlyRate]
    membership_status: MembershipStatus

    # TODO implement the rest of membership stuff.

    def __init__(self, data: Dict[str, Any]):
        self.user_id = data["userId"]
        self.target_id = data["targetId"]
        data_hourly_rate = data["hourlyRate"]
        self.hourly_rate = HourlyRate(data_hourly_rate) if data_hourly_rate else None
        self.membership_status = MembershipStatus.from_json(data["membershipStatus"])


@dataclass
class Workspace:
    uid: str
    name: str
    settings: Dict[str, Any]
    hourly_rate: HourlyRate
    image_url: str
    memberships: List[Membership]

    def __init__(self, data: Dict[str, Any]):
        self.uid = data["id"]
        self.name = data["name"]
        self.settings = data["workspaceSettings"]
        self.hourly_rate = HourlyRate(data["hourlyRate"])
        self.image_url = data["imageUrl"]
        self.memberships = [Membership(m) for m in data["memberships"]]


class UserStatus(Enum):
    ACTIVE = auto()
    PENDING_EMAIL_VERIFICATION = auto()
    DELETED = auto()

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "UserStatus":
        if data == "ACTIVE":
            return UserStatus.ACTIVE
        if data == "PENDING_EMAIL_VERIFICATION":
            return UserStatus.PENDING_EMAIL_VERIFICATION
        if data == "DELETED":
            return UserStatus.DELETED

        raise CannotDecodeException(data)


class EstimateType(Enum):
    AUTO = auto()
    MANUAL = auto()

    @staticmethod
    def from_json(data: str) -> "EstimateType":
        if data == "AUTO":
            return EstimateType.AUTO
        if data == "MANUAL":
            return EstimateType.MANUAL

        raise CannotDecodeException(data)


@dataclass
class Estimate:
    estimate: timedelta
    of_type: EstimateType

    def __init__(self, data: Dict[str, Any]):
        self.estimate = _estimate_to_timedelta(data["estimate"])
        self.of_type = data["type"]


@dataclass
class Client:
    uid: str
    name: str
    workspace_id: str

    def __init__(self, data: Dict[str, Any]):
        self.uid = data["id"]
        self.name = data["name"]
        self.workspace_id = data["workspaceId"]


class TaskStatus(Enum):
    DONE = auto()
    ACTIVE = auto()

    @staticmethod
    def from_json(data: str) -> "TaskStatus":
        if data == "DONE":
            return TaskStatus.DONE
        if data == "ACTIVE":
            return TaskStatus.ACTIVE

        raise CannotDecodeException(data)


@dataclass
class Task:
    uid: str
    assignee_id: str
    estimate: timedelta
    name: str
    project_id: str
    status: TaskStatus

    def __init__(self, data: Dict[str, Any]):
        self.uid = data["id"]
        self.assignee_id = data["assigneeId"]
        self.estimate = _estimate_to_timedelta(data["estimate"])
        self.name = data["name"]
        self.project_id = data["projectId"]
        self.status = TaskStatus.from_json(data["status"])


@dataclass
class TimeEntry:
    billable: bool
    locked: bool
    description: str
    project_id: Optional[str]
    tag_ids: List[str]
    task_id: Optional[str]
    start: datetime
    end: Optional[datetime]
    duration: Optional[timedelta]

    def __init__(self, data: Dict[str, Any]):
        self.billable = data["billable"] == "true"
        print(data)
        self.locked = data["isLocked"] == "true"
        self.description = data["description"]
        self.project_id = data["projectId"]
        self.tag_ids = data["tagIds"]
        self.task_id = data["taskId"]
        self.start = datetime.strptime(
            data["timeInterval"]["start"], "%Y-%m-%dT%H:%M:%SZ"
        )
        try:
            self.end = datetime.strptime(
                data["timeInterval"]["end"], "%Y-%m-%dT%H:%M:%SZ"
            )
        except TypeError:
            self.end = None
        if self.end:
            self.duration = self.end - self.start
        else:
            self.duration = None


@dataclass
class Project:
    uid: str
    name: str
    public: bool
    workspace_id: str
    client_id: Optional[str]
    archived: bool
    billable: bool
    color: str
    duration: timedelta
    estimate: Estimate
    hourly_rate: Optional[HourlyRate]
    memberships: List[Membership]

    def __init__(self, data: Dict[str, Any]):
        self.uid = data["id"]
        self.name = data["name"]
        self.public = data["public"] == "true"
        self.workspace_id = data["workspaceId"]
        self.archived = data["archived"] == "true"
        self.billable = data["billable"] == "true"
        self.client_id = data["clientId"]
        self.color = data["color"]
        data_hourly_rate = data["hourlyRate"]
        self.hourly_rate = HourlyRate(data["hourlyRate"]) if data_hourly_rate else None
        self.memberships = [Membership(m) for m in data["memberships"]]
        self.duration = _estimate_to_timedelta(data["duration"])
        self.estimate = Estimate(data["estimate"])


@dataclass
class User:
    active_workspace_id: str
    default_workspace_id: str
    email: str
    uid: str
    memberships: List[Membership]
    name: str
    profile_pic: str
    settings: Dict[str, Any]
    status: UserStatus

    def __init__(self, data: Dict[str, Any]):
        self.active_workspace_id = data["activeWorkspace"]
        self.default_workspace_id = data["defaultWorkspace"]
        self.email = data["email"]
        self.uid = data["id"]
        self.memberships = [Membership(m) for m in data["memberships"]]
        self.profile_pic = data["profilePicture"]
        self.settings = data["settings"]
        self.status = UserStatus.from_json(data["status"])
