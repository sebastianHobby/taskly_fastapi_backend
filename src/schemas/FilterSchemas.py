import enum
from typing import (
    Optional,
    List,
)
from uuid import UUID

from pydantic import ConfigDict, BaseModel, model_validator


# Schemas that define allowed parameters for each list type
# Using models as they allow the field to be validated using pydantic instead of just checking names
class RuleParmsTaskUnderList(BaseModel):
    list_id: Optional[UUID] = None


class RuleParmsTaskUnderListGroup(BaseModel):
    list_id: Optional[UUID] = None


# Enumeration defining all TaskFilterRules - The literal value here is shown in OpenAPI docs
class TaskFilterRuleTypes(enum.Enum):
    TaskUnderList = "TaskFilterByListId"
    TaskUnderListGroup = "TaskFilterByGroupId"


class TaskFilterRule(BaseModel):
    filter_rule_type: TaskFilterRuleTypes
    filter_rule_type: TaskFilterRuleTypes
    rule_parms: dict

    @model_validator(mode="after")
    def validate_parms_based_on_type(self):
        class_map = {
            TaskFilterRuleTypes.TaskUnderList: RuleParmsTaskUnderList,
            TaskFilterRuleTypes.TaskUnderListGroup: RuleParmsTaskUnderListGroup,
        }
        validation_class = class_map[self.filter_rule_type]
        if validation_class is None:
            raise ValueError("Expected parameter definition for filter rule not found")
        # Now validate by loading dictionary values into model
        validation_obj = validation_class.model_validate(
            self.rule_parms, from_attributes=True, extra="allow"
        )
        # Pydantic will store extra attributes in this variable when extra=allow as above
        if len(validation_obj.__pydantic_extra__.keys()) > 0:
            raise ValueError(
                f"Rule type {self.filter_rule_type.value} parms must be {validation_class.model_fields}"
            )

        return self


class FilterCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    task_filter_rules: List[TaskFilterRule]


class FilterResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    task_filter_rules: List[TaskFilterRule]


#
#
# class TaskFilterManager:
#     def __init__(self, config: Config):
#         self.config = config
#
#
# class FilterRule(BaseModel):
#     """Class used to represent a filter rule.
#     This is saved in database to allow users to customise specific rules for a view"""
#
#     ruleType: TaskFilterRuleTypes
#     named_parameters: dict
#
#
# class View(BaseModel):
#     view_name: str
#     filter_rules: List[FilterRule]
