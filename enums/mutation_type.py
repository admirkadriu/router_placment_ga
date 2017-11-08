from enum import Enum


class MutationType(Enum):
    SHIFT = 0
    CLEVER_SHIFT = 1
    RANDOM_MOVE = 2
    ADD_ROUTER = 3
    REMOVE_ROUTER = 4
