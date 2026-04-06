import copy
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple


def _fmt_time(minutes: int) -> str:
    """Convert minutes-from-midnight to a human-readable HH:MM string."""
    h, m = divmod(minutes, 60)
    return f"{h:02d}:{m:02d}"


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


class Recurrence(Enum):
    NONE = "none"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    title: str
    duration_minutes: int
    priority: Priority
    category: Category
    completed: bool = False
    time_slot: Optional[int] = None  # minutes from midnight (0–1439); None = unscheduled
    recurrence: Recurrence = Recurrence.NONE

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task as completed and return the next occurrence if recurring, else None."""
        self.completed = True
        if self.recurrence in (Recurrence.DAILY, Recurrence.WEEKLY):
            next_task = copy.copy(self)
            next_task.completed = False
            return next_task
        return None


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
    conflicts: List[str] = field(default_factory=list)
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
        """Generate a daily plan for the pet within the owner's available time budget.

        Pipeline:
          1. apply_age_boost  — elevates HEALTH task priority for young/senior pets.
          2. filter_by_time   — separates tasks that can never fit (impossible) from
                                those that might (schedulable).
          3. sort_by_priority — orders schedulable tasks so the most important ones
                                are considered first.
          4. Greedy fit       — walks the sorted list and adds each task if it fits
                                within remaining minutes; otherwise skips it. Skipping
                                one task does not stop later (shorter) tasks from being
                                scheduled.
          5. Time-slot sort   — reorders the final scheduled list chronologically so
                                timed tasks appear before unscheduled ones.
          6. detect_conflicts — scans the scheduled list for overlapping time windows
                                and records human-readable warning strings.

        Returns:
            A DailyPlan with scheduled_tasks, skipped_tasks, and any conflict warnings.
        """
        boosted = self.apply_age_boost(self.tasks)
        schedulable, impossible = self.filter_by_time(boosted)
        sorted_tasks = self.sort_by_priority(schedulable)
        plan = DailyPlan()
        plan.skipped_tasks.extend(impossible)
        for task in sorted_tasks:
            if plan.total_minutes_used + task.duration_minutes <= self.owner.available_minutes_per_day:
                plan.scheduled_tasks.append(task)
            else:
                plan.skipped_tasks.append(task)
        # Sort scheduled tasks by time_slot (timed tasks first, then unscheduled)
        plan.scheduled_tasks.sort(key=lambda t: (t.time_slot is None, t.time_slot or 0))
        plan.conflicts = self.detect_conflicts(plan.scheduled_tasks, pet_label=self.pet.name)
        return plan

    def apply_age_boost(self, tasks: List[Task]) -> List[Task]:
        """Elevate HEALTH tasks to HIGH priority for age-vulnerable pets.

        Pets younger than 2 or older than 8 are considered age-vulnerable. For those
        pets, any HEALTH task that isn't already HIGH priority receives a shallow copy
        with its priority set to HIGH. Non-HEALTH tasks and tasks already at HIGH are
        returned unchanged.

        Original Task objects are never mutated — copies are made so the caller's list
        is unaffected. If the pet's age is not in the vulnerable range, the original
        list is returned as-is with no copies made.

        Returns:
            A new list of Task objects with HEALTH priorities boosted where applicable.
        """
        if self.pet.age < 2 or self.pet.age > 8:
            boosted = []
            for task in tasks:
                if task.category == Category.HEALTH and task.priority != Priority.HIGH:
                    t = copy.copy(task)
                    t.priority = Priority.HIGH
                    boosted.append(t)
                else:
                    boosted.append(task)
            return boosted
        return tasks

    def filter_by_time(self, tasks: List[Task]) -> Tuple[List[Task], List[Task]]:
        """Split tasks into two buckets based on the owner's total daily time budget.

        A task is "impossible" if its duration alone exceeds available_minutes_per_day —
        it could never be scheduled regardless of what else is on the list. These are
        separated early so they can be reported to the owner with a clear reason, rather
        than silently disappearing after the greedy fit loop.

        A task is "schedulable" if its duration fits within the daily budget. It is not
        guaranteed to make the final plan — that depends on how much time is left after
        higher-priority tasks are scheduled.

        Returns:
            (schedulable, impossible) — two lists that together contain every input task.
        """
        schedulable = [t for t in tasks if t.duration_minutes <= self.owner.available_minutes_per_day]
        impossible = [t for t in tasks if t.duration_minutes > self.owner.available_minutes_per_day]
        return schedulable, impossible

    def sort_by_priority(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks using a three-level key so the most important work is scheduled first.

        Sort key (ascending, so lower numbers = scheduled earlier):
          1. Priority      — HIGH (0) → MEDIUM (1) → LOW (2).
          2. Recurrence    — DAILY (0) → WEEKLY (1) → NONE (2). Within the same priority
                             tier, recurring tasks are preferred so routine care is never
                             bumped by a one-off task of equal priority.
          3. Duration      — shorter tasks come first when priority and recurrence are equal.
                             This maximises the number of tasks that fit within the time
                             budget (a greedy bin-packing heuristic).

        Returns:
            A new sorted list; the original list is not modified.
        """
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        recurrence_order = {Recurrence.DAILY: 0, Recurrence.WEEKLY: 1, Recurrence.NONE: 2}
        return sorted(
            tasks,
            key=lambda t: (priority_order[t.priority], recurrence_order[t.recurrence], t.duration_minutes),
        )

    def reschedule_recurring(self, task: Task) -> Optional[Task]:
        """Return a fresh copy of a recurring task for its next occurrence, or None if not recurring.

        The caller is responsible for adding the returned task to the pet's task list,
        checking for duplicates before doing so.
        """
        if task.recurrence == Recurrence.NONE:
            return None
        next_task = copy.copy(task)
        next_task.completed = False
        return next_task

    def detect_conflicts(self, tasks: List[Task], pet_label: str = "") -> List[str]:
        """Return warning messages for same-pet tasks whose time slots overlap.

        Only tasks with a time_slot set are checked. Tasks without one are skipped
        rather than raising an error, keeping detection lightweight.
        """
        timed = [t for t in tasks if t.time_slot is not None]
        prefix = f"[{pet_label}] " if pet_label else ""
        warnings = []
        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                a, b = timed[i], timed[j]
                if a.time_slot < b.time_slot + b.duration_minutes and b.time_slot < a.time_slot + a.duration_minutes:
                    warnings.append(
                        f"{prefix}'{a.title}' ({_fmt_time(a.time_slot)}–{_fmt_time(a.time_slot + a.duration_minutes)})"
                        f" overlaps with '{b.title}' ({_fmt_time(b.time_slot)}–{_fmt_time(b.time_slot + b.duration_minutes)})"
                    )
        return warnings

    @staticmethod
    def detect_cross_pet_conflicts(pet_plans: Dict[str, List[Task]]) -> List[str]:
        """Return warning messages for tasks across different pets whose time slots overlap.

        Args:
            pet_plans: mapping of pet name → list of scheduled Task objects.

        Only timed tasks are compared. Returns an empty list (never raises) so the
        caller can display warnings without any risk of crashing the schedule view.
        """
        warnings = []
        pet_names = list(pet_plans.keys())
        for i in range(len(pet_names)):
            for j in range(i + 1, len(pet_names)):
                name_a, name_b = pet_names[i], pet_names[j]
                timed_a = [t for t in pet_plans[name_a] if t.time_slot is not None]
                timed_b = [t for t in pet_plans[name_b] if t.time_slot is not None]
                for a in timed_a:
                    for b in timed_b:
                        if a.time_slot < b.time_slot + b.duration_minutes and b.time_slot < a.time_slot + a.duration_minutes:
                            warnings.append(
                                f"Cross-pet conflict: '{a.title}' ({name_a}, {_fmt_time(a.time_slot)}–{_fmt_time(a.time_slot + a.duration_minutes)})"
                                f" overlaps with '{b.title}' ({name_b}, {_fmt_time(b.time_slot)}–{_fmt_time(b.time_slot + b.duration_minutes)})"
                            )
        return warnings
