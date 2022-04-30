import click

from typing import Callable, Tuple, TypeVar, Iterable, Any

from collections import OrderedDict
from collections.abc import Mapping

T = TypeVar("T")


class JunctionError(Exception):
    pass


def for_all(items: Iterable[T], action: Callable[[T], None]) -> None:
    """Runs a particular function for every item in a list.

    Arguments:
        items {List[T]} -- A list of items.
        action {Callable[[T], None]} -- A function to call which accepts a single item.
    """
    for item in items:
        action(item)


class DotDict(OrderedDict):
    """
    Quick and dirty implementation of a dot-able dict, which allows access and
    assignment via object properties rather than dict indexing.
    """

    def __init__(self, *args: Any, **kwargs: Any):
        # we could just call super(DotDict, self).__init__(*args, **kwargs)
        # but that won't get us nested dotdict objects
        od = OrderedDict(*args, **kwargs)
        for key, val in od.items():
            if isinstance(val, Mapping):
                value = DotDict(val)
            else:
                value = val
            self[key] = value

    def __delattr__(self, name: Any) -> None:
        try:
            del self[name]
        except KeyError as ex:
            raise AttributeError(f"No attribute called: {name}") from ex

    def __getattr__(self, k: Any) -> Any:
        try:
            return self[k]
        except KeyError as ex:
            raise AttributeError(f"No attribute called: {k}") from ex

    def __setattr__(self, __name: str, __value: Any) -> None:
        return super().__setattr__(__name, __value)


# inspired from https://stackoverflow.com/a/44349292
class NotRequiredIf(click.Option):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.not_required_if: list = kwargs.pop("not_required_if")
        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs["help"] = (
            kwargs.get("help", "")
            + " NOTE: This argument is mutually exclusive with %s"
            % self.not_required_if
        ).strip()
        super(NotRequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx: Any, opts: Any, args: Any) -> Tuple[Any, Any]:
        current_opt: bool = self.name in opts
        for opt in self.not_required_if:
            if opt in opts:
                if current_opt:
                    raise click.UsageError(
                        "Illegal usage: "
                        + "'{}' is mutually exclusive with '{}'".format(self.name, opt)
                    )
            else:
                self.prompt = None

        return super(NotRequiredIf, self).handle_parse_result(ctx, opts, args)
