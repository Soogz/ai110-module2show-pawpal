classDiagram
    class Task {
        +String title
        +int duration_minutes
        +String priority
        +String category
        +bool completed
    }

    class Pet {
        +String name
        +String species
        +int age
    }

    class Owner {
        +String name
        +int available_minutes_per_day
        +List preferences
    }

    class Scheduler {
        +Owner owner
        +Pet pet
        +List~Task~ tasks
        +generate_plan() DailyPlan
        +filter_by_time() List~Task~
        +sort_by_priority() List~Task~
    }

    class DailyPlan {
        +List~Task~ scheduled_tasks
        +List~Task~ skipped_tasks
        +int total_minutes_used
        +String explanation
        +display() void
    }

    Owner "1" --> "1" Pet : owns
    Owner "1" --> "many" Task : manages
    Scheduler --> Owner : uses
    Scheduler --> Pet : uses
    Scheduler --> Task : processes
    Scheduler --> DailyPlan : produces
    DailyPlan --> Task : contains