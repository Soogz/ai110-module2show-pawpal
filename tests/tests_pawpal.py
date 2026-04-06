import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Owner, Scheduler, Priority, Category, Recurrence


class TestMarkComplete(unittest.TestCase):
    def setUp(self):
        self.task = Task(
            title="Morning Walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            category=Category.EXERCISE,
        )

    def test_task_starts_incomplete(self):
        self.assertFalse(self.task.completed)

    def test_mark_complete_sets_completed_true(self):
        self.task.mark_complete()
        self.assertTrue(self.task.completed)

    def test_mark_complete_is_idempotent(self):
        self.task.mark_complete()
        self.task.mark_complete()
        self.assertTrue(self.task.completed)


class TestPetTaskCount(unittest.TestCase):
    def setUp(self):
        self.pet = Pet(name="Buddy", species="Dog", age=3)

    def test_pet_starts_with_no_tasks(self):
        self.assertEqual(len(self.pet.tasks), 0)

    def test_adding_one_task_increases_count(self):
        task = Task("Feed Breakfast", 10, Priority.HIGH, Category.FEEDING)
        self.pet.add_task(task)
        self.assertEqual(len(self.pet.tasks), 1)

    def test_adding_multiple_tasks_increases_count(self):
        tasks = [
            Task("Feed Breakfast", 10, Priority.HIGH, Category.FEEDING),
            Task("Brush Coat", 15, Priority.MEDIUM, Category.GROOMING),
            Task("Play Fetch", 20, Priority.LOW, Category.PLAY),
        ]
        for task in tasks:
            self.pet.add_task(task)
        self.assertEqual(len(self.pet.tasks), 3)

    def test_task_added_is_the_correct_task(self):
        task = Task("Vet Checkup", 45, Priority.HIGH, Category.HEALTH)
        self.pet.add_task(task)
        self.assertIn(task, self.pet.tasks)


# ---------------------------------------------------------------------------
# Helpers shared across new test classes
# ---------------------------------------------------------------------------

def _make_scheduler(tasks, budget=480, pet_age=3):
    pet = Pet(name="Rex", species="Dog", age=pet_age)
    owner = Owner(name="Alex", available_minutes_per_day=budget)
    return Scheduler(owner=owner, pet=pet, tasks=tasks)


# ---------------------------------------------------------------------------
# Sorting Correctness
# ---------------------------------------------------------------------------

class TestSortByPriority(unittest.TestCase):
    """Verify sort_by_priority orders tasks correctly and generate_plan
    returns scheduled tasks in chronological (time_slot) order."""

    def _scheduler(self, tasks, budget=480, age=3):
        return _make_scheduler(tasks, budget=budget, pet_age=age)

    def test_high_before_medium_before_low(self):
        tasks = [
            Task("Low Task",    10, Priority.LOW,    Category.PLAY),
            Task("Medium Task", 10, Priority.MEDIUM, Category.GROOMING),
            Task("High Task",   10, Priority.HIGH,   Category.FEEDING),
        ]
        s = self._scheduler(tasks)
        result = s.sort_by_priority(tasks)
        self.assertEqual(
            [t.priority for t in result],
            [Priority.HIGH, Priority.MEDIUM, Priority.LOW],
        )

    def test_daily_before_weekly_before_none_within_same_priority(self):
        tasks = [
            Task("One-off",  10, Priority.MEDIUM, Category.PLAY,     recurrence=Recurrence.NONE),
            Task("Weekly",   10, Priority.MEDIUM, Category.GROOMING, recurrence=Recurrence.WEEKLY),
            Task("Daily",    10, Priority.MEDIUM, Category.FEEDING,  recurrence=Recurrence.DAILY),
        ]
        s = self._scheduler(tasks)
        result = s.sort_by_priority(tasks)
        self.assertEqual(
            [t.recurrence for t in result],
            [Recurrence.DAILY, Recurrence.WEEKLY, Recurrence.NONE],
        )

    def test_shorter_duration_first_when_priority_and_recurrence_tied(self):
        tasks = [
            Task("Long",  60, Priority.HIGH, Category.EXERCISE),
            Task("Short", 10, Priority.HIGH, Category.EXERCISE),
        ]
        s = self._scheduler(tasks)
        result = s.sort_by_priority(tasks)
        self.assertEqual(result[0].title, "Short")
        self.assertEqual(result[1].title, "Long")

    def test_empty_task_list_returns_empty(self):
        s = self._scheduler([])
        self.assertEqual(s.sort_by_priority([]), [])

    def test_single_task_list_unchanged(self):
        task = Task("Solo", 20, Priority.LOW, Category.OTHER)
        s = self._scheduler([task])
        result = s.sort_by_priority([task])
        self.assertEqual(result, [task])

    def test_scheduled_tasks_ordered_chronologically(self):
        """generate_plan must return timed tasks sorted by time_slot ascending."""
        tasks = [
            Task("Late Task",  20, Priority.HIGH, Category.FEEDING,  time_slot=600),  # 10:00
            Task("Early Task", 20, Priority.HIGH, Category.EXERCISE, time_slot=60),   # 01:00
            Task("Mid Task",   20, Priority.HIGH, Category.GROOMING, time_slot=300),  # 05:00
        ]
        s = self._scheduler(tasks)
        plan = s.generate_plan()
        slots = [t.time_slot for t in plan.scheduled_tasks]
        self.assertEqual(slots, sorted(slots))

    def test_unscheduled_tasks_appear_after_timed_tasks(self):
        tasks = [
            Task("No Slot",   20, Priority.HIGH, Category.PLAY,    time_slot=None),
            Task("Has Slot",  20, Priority.HIGH, Category.FEEDING, time_slot=120),
        ]
        s = self._scheduler(tasks)
        plan = s.generate_plan()
        timed = [t for t in plan.scheduled_tasks if t.time_slot is not None]
        untimed = [t for t in plan.scheduled_tasks if t.time_slot is None]
        # All timed tasks must appear before any untimed task
        if timed and untimed:
            last_timed_idx = plan.scheduled_tasks.index(timed[-1])
            first_untimed_idx = plan.scheduled_tasks.index(untimed[0])
            self.assertLess(last_timed_idx, first_untimed_idx)


# ---------------------------------------------------------------------------
# Recurrence Logic
# ---------------------------------------------------------------------------

class TestRecurrenceLogic(unittest.TestCase):
    """Confirm that marking a recurring task complete produces a fresh occurrence."""

    def test_daily_task_returns_new_task_on_complete(self):
        task = Task("Daily Feed", 15, Priority.HIGH, Category.FEEDING, recurrence=Recurrence.DAILY)
        next_task = task.mark_complete()
        self.assertIsNotNone(next_task)

    def test_new_occurrence_is_not_completed(self):
        task = Task("Daily Feed", 15, Priority.HIGH, Category.FEEDING, recurrence=Recurrence.DAILY)
        next_task = task.mark_complete()
        self.assertFalse(next_task.completed)

    def test_original_task_is_marked_completed(self):
        task = Task("Daily Feed", 15, Priority.HIGH, Category.FEEDING, recurrence=Recurrence.DAILY)
        task.mark_complete()
        self.assertTrue(task.completed)

    def test_new_occurrence_is_a_different_object(self):
        task = Task("Daily Feed", 15, Priority.HIGH, Category.FEEDING, recurrence=Recurrence.DAILY)
        next_task = task.mark_complete()
        self.assertIsNot(task, next_task)

    def test_new_occurrence_preserves_title_and_duration(self):
        task = Task("Daily Feed", 15, Priority.HIGH, Category.FEEDING, recurrence=Recurrence.DAILY)
        next_task = task.mark_complete()
        self.assertEqual(next_task.title, task.title)
        self.assertEqual(next_task.duration_minutes, task.duration_minutes)

    def test_weekly_task_also_returns_new_occurrence(self):
        task = Task("Weekly Groom", 30, Priority.MEDIUM, Category.GROOMING, recurrence=Recurrence.WEEKLY)
        next_task = task.mark_complete()
        self.assertIsNotNone(next_task)
        self.assertFalse(next_task.completed)

    def test_non_recurring_task_returns_none_on_complete(self):
        task = Task("One-off Vet", 60, Priority.HIGH, Category.HEALTH, recurrence=Recurrence.NONE)
        result = task.mark_complete()
        self.assertIsNone(result)

    def test_completing_daily_task_twice_produces_two_independent_occurrences(self):
        task = Task("Daily Feed", 15, Priority.HIGH, Category.FEEDING, recurrence=Recurrence.DAILY)
        first = task.mark_complete()
        second = first.mark_complete()
        self.assertIsNotNone(second)
        self.assertIsNot(first, second)
        self.assertTrue(first.completed)
        self.assertFalse(second.completed)


# ---------------------------------------------------------------------------
# Conflict Detection
# ---------------------------------------------------------------------------

class TestConflictDetection(unittest.TestCase):
    """Verify detect_conflicts flags overlapping time slots and ignores valid schedules."""

    def _scheduler(self, tasks, budget=480, age=3):
        return _make_scheduler(tasks, budget=budget, pet_age=age)

    def test_overlapping_tasks_produce_conflict_warning(self):
        tasks = [
            Task("Walk",  60, Priority.HIGH, Category.EXERCISE, time_slot=60),   # 01:00–02:00
            Task("Feed",  30, Priority.HIGH, Category.FEEDING,  time_slot=90),   # 01:30–02:00 (overlaps)
        ]
        s = self._scheduler(tasks)
        warnings = s.detect_conflicts(tasks, pet_label="Rex")
        self.assertGreater(len(warnings), 0)

    def test_same_start_time_is_a_conflict(self):
        tasks = [
            Task("Task A", 30, Priority.HIGH, Category.FEEDING,  time_slot=120),
            Task("Task B", 30, Priority.HIGH, Category.EXERCISE, time_slot=120),
        ]
        s = self._scheduler(tasks)
        warnings = s.detect_conflicts(tasks)
        self.assertGreater(len(warnings), 0)

    def test_back_to_back_tasks_are_not_a_conflict(self):
        tasks = [
            Task("Walk", 30, Priority.HIGH, Category.EXERCISE, time_slot=60),   # 01:00–01:30
            Task("Feed", 30, Priority.HIGH, Category.FEEDING,  time_slot=90),   # 01:30–02:00
        ]
        s = self._scheduler(tasks)
        warnings = s.detect_conflicts(tasks)
        self.assertEqual(warnings, [])

    def test_non_overlapping_tasks_produce_no_warnings(self):
        tasks = [
            Task("Walk", 30, Priority.HIGH, Category.EXERCISE, time_slot=60),    # 01:00–01:30
            Task("Feed", 30, Priority.HIGH, Category.FEEDING,  time_slot=180),   # 03:00–03:30
        ]
        s = self._scheduler(tasks)
        warnings = s.detect_conflicts(tasks)
        self.assertEqual(warnings, [])

    def test_unscheduled_tasks_are_ignored_in_conflict_detection(self):
        tasks = [
            Task("No Slot A", 60, Priority.HIGH, Category.EXERCISE, time_slot=None),
            Task("No Slot B", 60, Priority.HIGH, Category.FEEDING,  time_slot=None),
        ]
        s = self._scheduler(tasks)
        warnings = s.detect_conflicts(tasks)
        self.assertEqual(warnings, [])

    def test_single_timed_task_has_no_conflict(self):
        tasks = [Task("Solo Walk", 30, Priority.HIGH, Category.EXERCISE, time_slot=60)]
        s = self._scheduler(tasks)
        warnings = s.detect_conflicts(tasks)
        self.assertEqual(warnings, [])

    def test_generate_plan_includes_conflict_in_plan_object(self):
        """End-to-end: generate_plan must surface overlapping tasks in plan.conflicts."""
        tasks = [
            Task("Walk",  60, Priority.HIGH, Category.EXERCISE, time_slot=60),
            Task("Feed",  30, Priority.HIGH, Category.FEEDING,  time_slot=90),
        ]
        s = self._scheduler(tasks, budget=200)
        plan = s.generate_plan()
        self.assertGreater(len(plan.conflicts), 0)

    def test_cross_pet_conflict_detected(self):
        task_a = Task("Walk Dog",  30, Priority.HIGH, Category.EXERCISE, time_slot=60)
        task_b = Task("Feed Cat",  30, Priority.HIGH, Category.FEEDING,  time_slot=75)  # overlaps
        warnings = Scheduler.detect_cross_pet_conflicts({"Dog": [task_a], "Cat": [task_b]})
        self.assertGreater(len(warnings), 0)

    def test_cross_pet_no_conflict_when_non_overlapping(self):
        task_a = Task("Walk Dog", 30, Priority.HIGH, Category.EXERCISE, time_slot=60)
        task_b = Task("Feed Cat", 30, Priority.HIGH, Category.FEEDING,  time_slot=180)
        warnings = Scheduler.detect_cross_pet_conflicts({"Dog": [task_a], "Cat": [task_b]})
        self.assertEqual(warnings, [])

    def test_cross_pet_single_pet_returns_no_warnings(self):
        task = Task("Walk", 30, Priority.HIGH, Category.EXERCISE, time_slot=60)
        warnings = Scheduler.detect_cross_pet_conflicts({"Dog": [task]})
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
