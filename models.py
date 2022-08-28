from aws_lambda_powertools.utilities.parser import BaseModel
from aws_lambda_powertools.utilities.parser import root_validator


# lifted and shifted from the moto3 library
def camelcase_to_underscores(argument: str):
    """Converts a camelcase param like theNewAttribute to the equivalent
    python underscore variable like the_new_attribute"""
    if argument.isupper():
        return argument.lower()

    result = ""
    prev_char_title = True
    if not argument:
        return argument
    for index, char in enumerate(argument):
        try:
            next_char_title = argument[index + 1].istitle()
        except IndexError:
            next_char_title = True

        upper_to_lower = char.istitle() and not next_char_title
        lower_to_upper = char.istitle() and not prev_char_title

        if index and (upper_to_lower or lower_to_upper):
            # Only add underscore if char is capital, not first letter, and next
            # char is not capital
            result += "_"
        prev_char_title = char.istitle()
        if not char.isspace():  # Only add non-whitespace
            result += char.lower()
    return result


class AWSSingleTableModel(BaseModel):
    """A base model that handles translations between AWS' naming conventions (for a single table
    model) and python's snake case"""

    _key = ""

    @classmethod
    def extra_conversions(cls, values):
        return values

    @root_validator(pre=True)
    def convert_pascal_case(cls, values):
        if "PK" in values:
            try:
                index = values["PK"].index("#") + 1
            except AttributeError:
                index = 0
            values[cls._key] = values["PK"][index:]
            for key in set(values) - {"SK", "PK", "GSI1PK", "GSI1SK"}:
                if key in values:
                    values[camelcase_to_underscores(key)] = values[key]
            values = cls.extra_conversions(values)
        return values


class Truck(AWSSingleTableModel):
    _key = "id"
    id: str
