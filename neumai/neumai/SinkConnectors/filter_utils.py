import re
from enum import Enum
from typing import Any, List
from pydantic import BaseModel, Field

OPERATOR_MAPPING = {
        "EQUAL": "=",
        "NOT_EQUAL": "!=",
        "LESS_THAN": "<",
        "LESS_THAN_OR_EQUAL": "<=",
        "GREATER_THAN": ">",
        "GREATER_THAN_OR_EQUAL": ">=",
        "IN": "IN",
        "NOT_IN": "NOT_IN",
        "BETWEEN": "BETWEEN",
        "NOT_BETWEEN": "NOT_BETWEEN",
        "LIKE": "LIKE",
        "NOT_LIKE": "NOT_LIKE",
        "IS_NULL": "IS_NULL",
        "IS_NOT_NULL": "IS_NOT_NULL"
    }

class FilterOperator(Enum):
    """
    Enum for filter operators.
    """

    EQUAL = "="
    NOT_EQUAL = "!="
    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    IN = "IN"
    NOT_IN = "NOT IN"
    BETWEEN = "BETWEEN"
    NOT_BETWEEN = "NOT BETWEEN"
    LIKE = "LIKE"
    NOT_LIKE = "NOT LIKE"
    IS_NULL = "IS NULL"
    IS_NOT_NULL = "IS NOT NULL"


class FilterCondition(BaseModel):
    """
    Base class for unified filter conditions, these need to be trans
    lated to the corressponding sink's filter conditions.
    """
    field:str = Field(..., description="Field to be filtered")
    operator:FilterOperator = Field(..., description="Operator for filter")
    value:str = Field(..., description="Value to filter field")


def dict_to_filter_condition(filter_dict: List[dict]) -> List[FilterCondition]:
    """Convert a filter string to a list of filter conditions

    Args:
        filter_dict (List[dict]): The filter dict list.
            Example:
            `
            [
                {
                    'field': 'field1',
                    'operator': 'op1',
                    'value': 'val1'
                },
                {
                    'field': 'field2',
                    'operator': 'op2',
                    'value': 'val2'
                }
            ]
            `
    Returns:
        List[FilterCondition]: A list of filter-condition objects.
    """

    filter_conditions = []
    for filter in filter_dict:
        op = filter["operator"]
        val = filter["value"]
        field = filter["field"]

        try:
            filter_conditions.append(
                FilterCondition(
                    field=field,
                    operator=OPERATOR_MAPPING[op],
                    value=val
                )
            )
        except:
            raise ValueError(f"Not a valid filter operation - {op}\n Supported operators are - {list(OPERATOR_MAPPING.keys())}")
    return filter_conditions
        
