classDiagram
    class Task {
        +String title
        +int duration_minutes
        +Priority priority
        +Category category
        +bool completed
        +Optional~int~ time_slot
        +Recurrence recurrence
        +mark_complete() Optional~Task~
    }

    class Pet {
        +String name
        +String species
        +int age
        +List~Task~ tasks
        +add_task(task Task) void
    }

    class Owner {
        +String name
        +int available_minutes_per_day
        +Optional~Pet~ pet
        +List~Task~ tasks
        +List~String~ preferences
        +__post_init__() void
    }

    class Scheduler {
        +Owner owner
        +Pet pet
        +List~Task~ tasks
        +generate_plan() DailyPlan
        +apply_age_boost() List~Task~
        +filter_by_time() List~Task~
        +sort_by_priority() List~Task~
        +reschedule_recurring() Optional~Task~
        +detect_conflicts() List~String~
        +detect_cross_pet_conflicts()$ List~String~
    }

    class DailyPlan {
        +List~Task~ scheduled_tasks
        +List~Task~ skipped_tasks
        +List~String~ conflicts
        +String explanation
        +total_minutes_used int
        +display() void
    }

    class Priority {
        <<enumeration>>
        HIGH
        MEDIUM
        LOW
    }

    class Category {
        <<enumeration>>
        FEEDING
        EXERCISE
        GROOMING
        HEALTH
        PLAY
        OTHER
    }

    class Recurrence {
        <<enumeration>>
        NONE
        DAILY
        WEEKLY
    }

    Pet "1" *-- "many" Task : owns
    Owner "1" o-- "0..1" Pet : has
    Scheduler --> Owner : uses
    Scheduler --> Pet : uses
    Scheduler --> Task : processes
    Scheduler --> DailyPlan : produces
    DailyPlan --> Task : contains
    Task --> Priority : has
    Task --> Category : has
    Task --> Recurrence : has
