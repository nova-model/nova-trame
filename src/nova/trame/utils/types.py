"""Custom types for nova-trame."""

from typing import Any, NamedTuple

from typing_extensions import Self


class TrameTuple(NamedTuple):
    """Trame variable binding tuple.

    Trame allows you to set component parameters dynamically by passing a tuple to most parameters. This tuple requires
    the following syntax: (expression, initial_value). expression is typically a JavaScript variable, but it can be any
    JavaScript expression that evaluates to a boolean value. initial_value should only used if your expression is a
    JavaScript variable.
    """

    expression: str
    initial_value: Any = None

    @classmethod
    def create(cls, expression: Any, initial_value: Any = None) -> Self:
        """Turns a generic expression into a tuple suitable for binding a Trame component.

        This is primarily intended for internal usage and makes aggressive assumptions about how to convert Python types
        to JavaScript expressions. If you are creating your own components with parameters that accept built-in types
        and Trame binding tuples, then it may prove useful to you either as is or subclassed.

        Parameters
        ----------
        expression : Any
            The content to turn into a JavaScript expression. If a string-type is provided, it is passed to Trame
            without modification.
        initial_value: Any, optional
            The initial value to assign to expression. If set, expression must be a JavaScript variable.
        """
        if (
            isinstance(expression, tuple)
            and len(expression) > 0
            and len(expression) < 3
            and isinstance(expression[0], str)
        ):
            # This looks like a Trame-style tuple, we should treat it accordingly.
            if len(expression) == 2:
                initial_value = expression[1]
            expression = expression[0]

        if isinstance(expression, (bool, complex, float, int)):
            if expression:
                return cls("true")
            else:
                return cls("false")

        return cls(str(expression), initial_value)
