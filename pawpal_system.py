from dataclasses import dataclass, field
from enum import Enum
from typing import List


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Category(Enum):
    FEEDING = "feeding"
    EXERCISE = "exercise"
    GROOMING = "grooming"
    HEALTH = "health"
    PLAY = "play"
    OTHER = "other"


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    category: Category
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True


@dataclass
class Pet:
    name: str
    species: str
    age: int
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)


@dataclass
class Owner:
    name: str
    available_minutes_per_day: int
    pet: Pet = None
    tasks: List[Task] = field(default_factory=list)
    preferences: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate that available_minutes_per_day is a positive integer."""
        if self.available_minutes_per_day <= 0:
            raise ValueError("available_minutes_per_day must be a positive integer")


@dataclass
class DailyPlan:
    scheduled_tasks: List[Task] = field(default_factory=list)
    skipped_tasks: List[Task] = field(default_factory=list)
    explanation: str = ""

    @property
    def total_minutes_used(self) -> int:
        """Return the total minutes used by all scheduled tasks."""
        return sum(t.duration_minutes for t in self.scheduled_tasks)

    def display(self) -> None:
        """Print the daily plan including scheduled and skipped tasks."""
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: List[Task]):
        """Initialize the scheduler with an owner, pet, and list of tasks."""
        self.owner = owner
        self.pet = pet
        self.tasks = list(tasks)  # shallow copy to avoid mutating caller's list

    def generate_plan(self) -> DailyPlan:
        """Generate a daily plan by filtering and scheduling tasks within available time."""
        filtered = self.filter_by_time(self.tasks)
        sorted_tasks = self.sort_by_priority(filtered)
        plan = DailyPlan()
        for task in sorted_tasks:
            if plan.total_minutes_used + task.duration_minutes <= self.owner.available_minutes_per_day:
                plan.scheduled_tasks.append(task)
            else:
                plan.skipped_tasks.append(task)
        return plan

    def filter_by_time(self, tasks: List[Task]) -> List[Task]:
        """Return only tasks that fit within the owner's available minutes per day."""
        return [t for t in tasks if t.duration_minutes <= self.owner.available_minutes_per_day]

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Return tasks sorted from highest to lowest priority."""
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(tasks, key=lambda t: order[t.priority])
