from typing import NamedTuple

from ._directive import Directive
from ._handler import SupervisionHandler


class SupervisionStrategy(NamedTuple):
    strategy: Directive
    maxNumOfRetries: int
    supervisionHandler: SupervisionHandler
