from enum import Enum


class TaskAndProjectStatuses(Enum):
    not_started = "Not started"
    in_progress = "In Progress"
    completed = "Completed"


class ProjectTypes(Enum):
    """Projects types define what fields are allowed.
    Projects - allow all fields including startdate/deadline
    Areas - allows only name and description. These represent areas of focus/life values
    """

    project = "project"
    area = "area"


class RepeatIntervalType(Enum):
    no_repeat = "noRepeat"
    from_last_completed_date = "fromLastCompletedDate"
    from_repeat_start_date = "fromRepeatStartDate"
