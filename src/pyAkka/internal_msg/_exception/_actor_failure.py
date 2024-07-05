from typing import NamedTuple

import pykka

from Common.ActorModel.PyAkka import SupervisionStrategy


class ActorFailureMessage(NamedTuple):
    supervision: SupervisionStrategy
    actor_ref: pykka.ActorRef

