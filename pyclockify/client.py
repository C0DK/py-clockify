"""
The direct client of the Clockify API
This creates direct requests to Clockify, and is the raw interface.
"""

from typing import Dict, Any, List, Union
import urllib.parse
from json import JSONDecodeError

import requests

from .dataclasses import Workspace, User, Project, Task, Tag, TimeEntry, Client

BASE_URL = "https://api.clockify.me/api/v1/"


class UnauthorizedRequest(Exception):
    """
    When a request to some Clockify element is Unauthorized
    """


class ForbiddenRequest(Exception):
    """
    When a request to some Clockify element is Forbidden
    """


class NotFoundException(Exception):
    """
    When the element trying to be fetched is not found
    """


class ResponseNotJsonException(Exception):
    """
    Thrown when response from Clockify isn't JSON and therefore cannot be decoded.
    """


class ClockifyClient:
    """"
    The base client of the system.
    This hooks up with the API directly
    And returns objects of each type in the API.
    """

    def __init__(self, api_key: str):
        """
        Initialize a client of the API
        """
        self.api_key = api_key

    def workspaces(self) -> List[Workspace]:
        """
        Find workspaces for currently logged in user
        :return: List of workspaces
        """
        data = self._req("workspaces")

        return [Workspace(e) for e in data]

    def time_entries(
        self, workspace: Union[str, Workspace], user: Union[str, User] = None
    ) -> List[TimeEntry]:
        """

        :param workspace:
        :param user:
        :return:
        """
        if isinstance(workspace, Workspace):
            workspace = workspace.uid
        if user is None:
            user = self.user()
        if isinstance(user, User):
            user = user.uid
        data = self._req(f"workspaces/{workspace}/user/{user}/time-entries")

        return [TimeEntry(t) for t in data]

    def user(self) -> User:
        """
        Get currently logged in user's info
        :return: User object
        """
        data = self._req("user")

        return User(data)

    def clients(self, workspace: Union[str, Workspace]) -> List[Client]:
        """
        Find tags on workspace
        :param workspace: the workspace to find tags on
        :return: list of tags
        """
        if isinstance(workspace, Workspace):
            workspace = workspace.uid

        data = self._req(f"workspaces/{workspace}/clients")

        return [Client(p) for p in data]

    def tags(self, workspace: Union[str, Workspace]) -> List[Tag]:
        """
        Find tags on workspace
        :param workspace: the workspace to find tags on
        :return: list of tags
        """
        if isinstance(workspace, Workspace):
            workspace = workspace.uid

        data = self._req(f"workspaces/{workspace}/tags")

        return [Tag(p) for p in data]

    def projects(self, workspace: Union[str, Workspace]) -> List[Project]:
        """
        Find projects on workspace
        :param workspace: the workspace to find projects on
        :return: list of projects
        """
        if isinstance(workspace, Workspace):
            workspace = workspace.uid

        data = self._req(f"workspaces/{workspace}/projects")

        return [Project(p) for p in data]

    def tasks(
        self, workspace: Union[str, Workspace], project: Union[str, Project]
    ) -> List[Task]:
        """
        Find tasks on project
        :param project: The project to look for tasks on
        :param workspace: the workspace to find projects on
        :return: list of tasks
        """
        if isinstance(workspace, Workspace):
            workspace = workspace.uid
        if isinstance(project, Project):
            project = project.uid

        data = self._req(f"workspaces/{workspace}/projects/{project}/tasks")
        return [Task(t) for t in data]

    def _req(
        self, endpoint: str, post_data: Dict[str, Any] = None
    ) -> Union[Dict[str, Any], List[Any]]:
        """
        Ba
        :param endpoint:
        :param post_data:
        :return:
        """
        headers = {"X-Api-Key": self.api_key, "content-type": "application/json"}
        path = urllib.parse.urljoin(BASE_URL, endpoint)
        if post_data is not None:
            resp = requests.post(path, headers=headers, json=post_data)
        else:
            resp = requests.get(path, headers=headers)

        if resp.status_code == 401:
            raise UnauthorizedRequest()
        if resp.status_code == 403:
            raise ForbiddenRequest()
        if resp.status_code == 404:
            raise NotFoundException(path)
        try:
            return resp.json()
        except JSONDecodeError:
            raise ResponseNotJsonException(
                f"Could not decode JSON\n {path} = {resp.content}"
            )
