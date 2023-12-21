import re
from enum import Enum
from typing import Any, List

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


class FilterCondition:
    """
    Base class for unified filter conditions, these need to be trans
    lated to the corressponding sink's filter conditions.
    """

    def __init__(self, column: str, operator: FilterOperator, value: Any):
        self.column = column
        self.operator = operator
        self.value = value

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, FilterCondition):
            return (
                self.column == __value.column
                and self.operator == __value.operator
                and self.value == __value.value
            )
        else:
            return False

    def __repr__(self) -> str:
        return f"""
            FilterCondition(
                column={self.column},
                operator={self.operator},
                value={self.value}
            )
        """

def string_to_filter_condition(filter_string: str) -> List[FilterCondition]:
    """Convert a filter string to a list of filter conditions

    Args:
        filter_string (str): The filter string.
            Example:
            `field1 <= value1, field2 != value2`
    Returns:
        List[FilterCondition]: A list of filter-condition objects.
    """

    # Parsing the string
    conditions = filter_string.split(",")
    
    # We can later add more operations
    ops = ['=', '!=', '<', '>', '<=', '>=']
    r = re.compile( '|'.join( '(?:{})'.format(re.escape(o)) for o in sorted(ops, reverse=True, key=len)) )

    filter_conditions = []
    for condition in conditions:
        # condition would be like 
        # `field1 <= value1`, or `field1<=value1` or `field1 <=value1` or `field1<= value1`
        op = r.findall(condition)[0]
        colval = condition.split(op)
        column = colval[0].strip()
        value = colval[1].strip()

        filter_conditions.append(
            FilterCondition(
                column=column,
                operator=op,
                value=value
            )
        )
    return filter_conditions
        
