from typing import NamedTuple, Tuple, Any

from Common.ActorModel.PyAkka import SupervisionStrategy


class ActorProp(NamedTuple):
    args: Tuple[Any, ...]
    kwargs: dict[str, Any]
