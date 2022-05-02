from typing import Tuple


class FarmParcours:
    def __init__(self, startMapId: int, path: list[Tuple[int, int]], skills: list[int]):
        self.startMapId = startMapId
        self.path = path
        self.skills = skills
