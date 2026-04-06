from pawpal_system import Owner, Pet, Task, Priority, Category, Scheduler


def print_plan(pet: Pet, plan) -> None:
    print(f"\n--- {pet.name}'s Schedule ---")
    if plan.scheduled_tasks:
        for task in plan.scheduled_tasks:
            status = "[x]" if task.completed else "[ ]"
            print(f"  {status} {task.title} ({task.duration_minutes} min) [{task.priority.value}]")
    else:
        print("  No tasks scheduled.")

    print(f"  Total time: {plan.total_minutes_used} min")

    if plan.skipped_tasks:
        print("  Skipped (not enough time):")
        for task in plan.skipped_tasks:
            print(f"    - {task.title} ({task.duration_minutes} min)")


def main():
    # Create two pets
    buddy = Pet(name="Buddy", species="Dog", age=3)
    whiskers = Pet(name="Whiskers", species="Cat", age=5)

    # Create owner with 60 available minutes per day
    owner = Owner(name="Alex", available_minutes_per_day=60, pet=buddy)

    # Tasks for Buddy (dog)
    buddy_tasks = [
        Task("Morning Walk",       duration_minutes=30, priority=Priority.HIGH,   category=Category.EXERCISE),
        Task("Feed Breakfast",     duration_minutes=10, priority=Priority.HIGH,   category=Category.FEEDING),
        Task("Brush Coat",         duration_minutes=15, priority=Priority.MEDIUM, category=Category.GROOMING),
        Task("Fetch in Backyard",  duration_minutes=20, priority=Priority.LOW,    category=Category.PLAY),
    ]

    # Tasks for Whiskers (cat)
    whiskers_tasks = [
        Task("Feed Dinner",        duration_minutes=5,  priority=Priority.HIGH,   category=Category.FEEDING),
        Task("Vet Checkup",        duration_minutes=45, priority=Priority.HIGH,   category=Category.HEALTH),
        Task("Laser Pointer Play", duration_minutes=10, priority=Priority.MEDIUM, category=Category.PLAY),
    ]

    print("=" * 40)
    print("        Today's Schedule — PawPal+")
    print("=" * 40)
    print(f"Owner : {owner.name}")
    print(f"Time  : {owner.available_minutes_per_day} min available today")

    for pet, tasks in [(buddy, buddy_tasks), (whiskers, whiskers_tasks)]:
        scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)
        plan = scheduler.generate_plan()
        print_plan(pet, plan)

    print("\n" + "=" * 40)


if __name__ == "__main__":
    main()
