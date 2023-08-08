"""Parameter Validator.

# Features:

- check param value in allowed list of str|int|float|complex
- check param value in between range of int|float
- check param value is valid if required
- custom exception type pickable

# Reference: https://pypi.org/project/pyvalidate/
# TODO: decorator?


"""

import pickle
from typing import Any, Union


class InvalidParamError(Exception):
    """Invalid Parameter Exception."""

    def __init__(self, method: str, name: str, value: Any) -> None:
        """Init."""
        self.method = method
        self.name = name
        self.value = value

        message = "Invalid Param: `{}` @ Method: `{}` with error Value: `{}`!".format(name, method, value)
        super(InvalidParamError, self).__init__(message)

        self.message = message

    def __reduce__(self):
        return (InvalidParamError, (self.method, self.name, self.value))



class ParamValidator:
    """Parameter Validator."""

    @classmethod
    def is_allowed_str(cls, name: str, value: str, allowed: list[str]) -> bool:
        """Check if param value in allowed list of str."""
        if allowed and value in allowed:
            return True

        raise InvalidParamError(
            method="is_allowed_str",
            name=name,
            value=value,
        )

    @classmethod
    def is_allowed_int(cls, name: str, value: int, allowed: list[int]) -> bool:
        """Check if param value in allowed list of int."""
        if allowed and value in allowed:
            return True

        raise InvalidParamError(
            method="is_allowed_int",
            name=name,
            value=value,
        )


    @classmethod
    def is_allowed_float(cls, name: str, value: float, allowed: list[float]) -> bool:
        """Check if param value in allowed list of float."""
        if allowed and value in allowed:
            return True

        raise InvalidParamError(
            method="is_allowed_float",
            name=name,
            value=value,
        )

    @classmethod
    def is_allowed_complex(cls, name: str, value: complex, allowed: list[int]) -> bool:
        """Check if param value in allowed list of complex."""
        if allowed and value in allowed:
            return True

        raise InvalidParamError(
            method="is_allowed_complex",
            name=name,
            value=value,
        )

    @classmethod
    def is_allowed(cls,
                   name: str,
                   value: Union[str, int, float],
                   allowed: list[Union[str, int, float]]) -> bool:
        """Check if param value in allowed list."""
        if isinstance(allowed, list) and allowed:
            if (
                isinstance(value, str)
                and isinstance(allowed[0], str)
            ):
                return cls.is_allowed_str(
                    name=name,
                    value=value,
                    allowed=allowed,
                )

            if isinstance(value, int):
                return cls.is_allowed_int(
                    name=name,
                    value=value,
                    allowed=allowed,
                )

            if isinstance(value, float):
                return cls.is_allowed_float(
                    name=name,
                    value=value,
                    allowed=allowed,
                )

            if isinstance(value, complex):
                return cls.is_allowed_complex(
                    name=name,
                    value=value,
                    allowed=allowed,
                )

        raise InvalidParamError(
            method="is_allowed",
            name=name,
            value=value,
        )

    @classmethod
    def is_between(cls,
                name: str,
                value: Union[int, float],
                left: Union[int, float],
                right: Union[int, float],
                weight: str = "none") -> bool:
        """Check if param value between(left, right)."""
        allowed_weight = ["none", "left", "right", "both"]

        if cls.is_allowed(
            name="weight",
            value=weight,
            allowed=allowed_weight
        ):
            return True

        if weight == "none" and left < value < right:
            return True

        if weight == "left" and left <= value < right:
            return True

        if weight == "right" and left < value <= right:
            return True

        if weight == "both" and left <= value <= right:
            return True

        raise InvalidParamError(
            method="is_between",
            name=name,
            value=value,
        )

    @classmethod
    def is_required(cls, name: str, value: Any) -> bool:
        """Check Param required has value set."""
        if isinstance(value, dict) and value != {}:
            return True

        if isinstance(value, list) and value != []:
            return True

        if isinstance(value, set) and value != set():
            return True

        if isinstance(value, str) and value != "":
            return True

        if value is not None:
            return True

        raise InvalidParamError(
            method="is_required",
            name=name,
            value=value,
        )



class TestParamValidator:
    """Test ParamValidator."""

    app = ParamValidator()

    def test_error_pickable(self) -> None:
        """Test Error pickable."""
        err = InvalidParamError(method="foo", name="bar", value="hello")

        print(repr(err))
        print(err.method)
        print(err.name)
        print(err.value)
        print(err.message)

        err2 = pickle.loads(pickle.dumps(err))
        print(repr(err2))
        print(err2.method)
        print(err2.name)
        print(err2.value)
        print(err2.message)

    def run_test(self) -> None:
        """Run Test."""
        self.test_error_pickable()


if __name__ == "__main__":
    TestParamValidator().run_test()