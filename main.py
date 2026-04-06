from pawpal_system import Owner, Pet, Task, Priority, Category, Scheduler


def print_task_list(tasks, label="Tasks"):
    print(f"\n  {label}:")
    if tasks:
        for task in tasks:
            print(f"    - {task.title:25s} ({task.duration_minutes:3d} min) [{task.priority.value}]")
    else:
        print("    (none)")


def print_plan(pet: Pet, plan) -> None:
    print(f"\n--- {pet.name}'s Final Schedule ---")
    if plan.scheduled_tasks:
        for task in plan.scheduled_tasks:
            status = "[x]" if task.completed else "[ ]"
            slot = f" @ {task.time_slot // 60:02d}:{task.time_slot % 60:02d}" if task.time_slot is not None else ""
            print(f"  {status} {task.title} ({task.duration_minutes} min) [{task.priority.value}]{slot}")
    else:
        print("  No tasks scheduled.")

    print(f"  Total time: {plan.total_minutes_used} min")

    if plan.skipped_tasks:
        print("  Skipped (not enough time):")
        for task in plan.skipped_tasks:
            print(f"    - {task.title} ({task.duration_minutes} min)")

    if plan.conflicts:
        print("  *** CONFLICTS DETECTED ***")
        for warning in plan.conflicts:
            print(f"    ! {warning}")


def main():
    # Create two pets
    buddy = Pet(name="Buddy", species="Dog", age=3)
    whiskers = Pet(name="Whiskers", species="Cat", age=5)

    # Create owner with 60 available minutes per day
    owner = Owner(name="Alex", available_minutes_per_day=60, pet=buddy)

    # Tasks added OUT OF ORDER (low → medium → high, mixed intentionally)
    # Feed Breakfast @ 08:00 (480) and Morning Walk @ 08:05 (485) intentionally overlap
    # to trigger detect_conflicts (breakfast ends at 08:10, walk starts at 08:05)
    buddy_tasks = [
        Task("Fetch in Backyard",  duration_minutes=20, priority=Priority.LOW,    category=Category.PLAY),
        Task("Brush Coat",         duration_minutes=15, priority=Priority.MEDIUM, category=Category.GROOMING),
        Task("Feed Breakfast",     duration_minutes=10, priority=Priority.HIGH,   category=Category.FEEDING,  time_slot=480),  # 08:00
        Task("Morning Walk",       duration_minutes=30, priority=Priority.HIGH,   category=Category.EXERCISE, time_slot=485),  # 08:05 — overlaps!
    ]

    # Tasks added OUT OF ORDER (medium → high → high, mixed intentionally)
    # Also includes one impossible task (90 min > 60 min budget) to test filter_by_time
    whiskers_tasks = [
        Task("Laser Pointer Play", duration_minutes=10, priority=Priority.MEDIUM, category=Category.PLAY),
        Task("Vet Checkup",        duration_minutes=45, priority=Priority.HIGH,   category=Category.HEALTH),
        Task("Feed Dinner",        duration_minutes=5,  priority=Priority.HIGH,   category=Category.FEEDING),
        Task("Full Grooming Spa",  duration_minutes=90, priority=Priority.LOW,    category=Category.GROOMING),  # impossible
    ]

    print("=" * 40)
    print("        Today's Schedule — PawPal+")
    print("=" * 40)
    print(f"Owner : {owner.name}")
    print(f"Time  : {owner.available_minutes_per_day} min available today")

    for pet, tasks in [(buddy, buddy_tasks), (whiskers, whiskers_tasks)]:
        scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)

        print(f"\n{'=' * 40}")
        print(f"  {pet.name} ({pet.species}, age {pet.age})")
        print(f"{'=' * 40}")

        # Show tasks as added (out of order)
        print_task_list(tasks, label="Tasks as added (out of order)")

        # Demonstrate filter_by_time
        schedulable, impossible = scheduler.filter_by_time(tasks)
        print_task_list(schedulable, label="After filter_by_time → schedulable")
        print_task_list(impossible,  label="After filter_by_time → impossible (exceed daily budget)")

        # Demonstrate sort_by_priority
        sorted_tasks = scheduler.sort_by_priority(schedulable)
        print_task_list(sorted_tasks, label="After sort_by_priority → sorted")

        # Generate and display the final plan
        plan = scheduler.generate_plan()
        print_plan(pet, plan)

    print("\n" + "=" * 40)


if __name__ == "__main__":
    main()
