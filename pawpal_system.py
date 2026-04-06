from dataclasses import dataclass, field
from typing import List


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: str
    category: str
    completed: bool = False


@dataclass
class Pet:
    name: str
    species: str
    age: int


@dataclass
class Owner:
    name: str
    available_minutes_per_day: int
    preferences: List[str] = field(default_factory=list)


@dataclass
class DailyPlan:
    scheduled_tasks: List[Task] = field(default_factory=list)
    skipped_tasks: List[Task] = field(default_factory=list)
    total_minutes_used: int = 0
    explanation: str = ""

    def display(self) -> None:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: List[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate_plan(self) -> DailyPlan:
        pass

    def filter_by_time(self) -> List[Task]:
        pass

    def sort_by_priority(self) -> List[Task]:
        pass
