import enum
from enum import Enum


class TaskAndProjectStatuses(Enum):
    not_started = "Not started"
    in_progress = "Started"
    completed = "Completed"


class ProjectTypes(Enum):
    """Project types define what fields are allowed.
    Projects - allow all fields including startdate/deadline
    Areas - allows only name and description. These represent areas of focus/life values
    """

    project = "project"
    area = "area"


class FilterTypes(enum.Enum):
    Project = enum.auto()
    Task = enum.auto()
