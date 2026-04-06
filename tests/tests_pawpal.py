import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, Priority, Category


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


if __name__ == "__main__":
    unittest.main()
