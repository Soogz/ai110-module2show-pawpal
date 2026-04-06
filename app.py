import streamlit as st
from pawpal_system import Owner, Pet, Task, Priority, Category, Recurrence, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("PawPal+")
st.subheader("Today's Pet Care Schedule")

# --- Session state init ---
if "pets" not in st.session_state:
    st.session_state.pets = []  # list of {"pet": Pet, "tasks": [Task]}
if "task_done" not in st.session_state:
    st.session_state.task_done = {}  # key: f"{pet_name}_{task_title}" -> bool
if "task_registry" not in st.session_state:
    st.session_state.task_registry = {}  # key: f"{pet_name}_{task_title}" -> Task

# --- Owner info ---
st.header("Owner Info")
owner_name = st.text_input("Your Name", value="")
available_minutes = st.number_input("Available Minutes Per Day", min_value=1, value=60)

st.divider()

# --- Add a pet ---
st.header("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet Name")
    species = st.text_input("Species (e.g. Dog, Cat)")
    age = st.number_input("Age", min_value=0, value=1)
    submitted = st.form_submit_button("Add Pet")
    if submitted:
        if pet_name and species:
            existing_names = [e["pet"].name for e in st.session_state.pets]
            if pet_name in existing_names:
                st.warning(f"A pet named '{pet_name}' already exists.")
            else:
                st.session_state.pets.append({"pet": Pet(name=pet_name, species=species, age=age), "tasks": []})
                st.success(f"{pet_name} added!")
        else:
            st.warning("Please enter a pet name and species.")

st.divider()

# --- Add tasks to each pet ---
if st.session_state.pets:
    st.header("Add Tasks to Pets")
    pet_names = sorted([entry["pet"].name for entry in st.session_state.pets])
    selected_pet_name = st.selectbox("Select Pet", pet_names)
    selected_entry = next(e for e in st.session_state.pets if e["pet"].name == selected_pet_name)

    with st.form("add_task_form", clear_on_submit=True):
        task_title = st.text_input("Task Title")
        duration = st.number_input("Duration (minutes)", min_value=1, value=15)
        priority = st.selectbox("Priority", [p.value for p in Priority])
        category = st.selectbox("Category", [c.value for c in Category])
        recurrence = st.selectbox("Recurrence", [r.value for r in Recurrence])
        set_time = st.checkbox("Set specific time slot?")
        time_input = st.time_input("Time Slot", disabled=not set_time)
        task_submitted = st.form_submit_button("Add Task")
        if task_submitted:
            if task_title:
                time_slot = (time_input.hour * 60 + time_input.minute) if set_time else None
                task = Task(
                    title=task_title,
                    duration_minutes=int(duration),
                    priority=Priority(priority),
                    category=Category(category),
                    recurrence=Recurrence(recurrence),
                    time_slot=time_slot,
                )
                selected_entry["tasks"].append(task)
                st.session_state.task_registry[f"{selected_pet_name}_{task_title}"] = task
                st.success(f"Task '{task_title}' added to {selected_pet_name}!")
            else:
                st.warning("Please enter a task title.")

    # Time budget summary
    task_total = sum(t.duration_minutes for t in selected_entry["tasks"])
    remaining = available_minutes - task_total
    st.caption(
        f"Task total: {task_total} min | Budget: {available_minutes} min | "
        f"{'Remaining: ' + str(remaining) + ' min' if remaining >= 0 else 'Over budget by ' + str(-remaining) + ' min'}"
    )

    st.divider()

# --- Generate schedule ---
if st.session_state.pets and owner_name:
    st.header("Schedule")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        pet_filter = st.selectbox(
            "Filter by pet",
            ["All pets"] + sorted([e["pet"].name for e in st.session_state.pets]),
        )
    with col2:
        status_filter = st.radio("Show tasks", ["All", "Incomplete only"], horizontal=True)

    if st.button("Generate Schedule"):
        owner = Owner(name=owner_name, available_minutes_per_day=available_minutes)
        pet_scheduled: dict = {}  # pet name → scheduled tasks, for cross-pet detection
        for entry in st.session_state.pets:
            pet = entry["pet"]

            # Apply pet filter
            if pet_filter != "All pets" and pet.name != pet_filter:
                continue

            tasks = entry["tasks"]
            if not tasks:
                st.info(f"{pet.name} has no tasks.")
                continue

            scheduler = Scheduler(owner=owner, pet=pet, tasks=tasks)
            plan = scheduler.generate_plan()
            pet_scheduled[pet.name] = plan.scheduled_tasks

            st.subheader(f"{pet.name}'s Schedule ({pet.species}, age {pet.age})")

            # Same-pet conflict warnings
            for msg in plan.conflicts:
                st.warning(msg)

            if plan.scheduled_tasks:
                displayed = [
                    t for t in plan.scheduled_tasks
                    if status_filter == "All" or not st.session_state.task_done.get(f"{pet.name}_{t.title}", t.completed)
                ]
                for task in displayed:
                    cb_key = f"{pet.name}_{task.title}"
                    # Register so recurring logic can find the Task object
                    st.session_state.task_registry[cb_key] = task
                    # Build label with optional time and recurrence badge
                    time_str = ""
                    if task.time_slot is not None:
                        h, m = divmod(task.time_slot, 60)
                        time_str = f" @ {h:02d}:{m:02d}"
                    recur_str = f" [{task.recurrence.value}]" if task.recurrence != Recurrence.NONE else ""
                    label = (
                        f"{task.title}{time_str} — {task.duration_minutes} min "
                        f"[{task.priority.value}] [{task.category.value}]{recur_str}"
                    )
                    was_done = st.session_state.task_done.get(cb_key, task.completed)
                    checked = st.checkbox(label, value=was_done, key=cb_key)
                    st.session_state.task_done[cb_key] = checked

                    # Detect unchecked → checked transition for recurring tasks
                    if checked and not was_done:
                        next_task = task.mark_complete()
                        if next_task is not None:
                            pet_entry = next(e for e in st.session_state.pets if e["pet"].name == pet.name)
                            already_pending = any(
                                t.title == next_task.title and not t.completed
                                for t in pet_entry["tasks"]
                            )
                            if not already_pending:
                                pet_entry["tasks"].append(next_task)
                                st.session_state.task_registry[cb_key] = next_task
                                st.info(
                                    f"Next {task.recurrence.value} occurrence of '{task.title}' queued."
                                )
                st.caption(f"Total time: {plan.total_minutes_used} min")
            else:
                st.info("No tasks fit within the available time.")

            if plan.skipped_tasks:
                with st.expander("Skipped tasks"):
                    for task in plan.skipped_tasks:
                        reason = "exceeds daily budget" if task.duration_minutes > available_minutes else "not enough time"
                        st.write(f"- {task.title} ({task.duration_minutes} min) — {reason}")

            st.divider()

        # Cross-pet conflict warnings (shown once, after all per-pet schedules)
        if len(pet_scheduled) > 1:
            cross_warnings = Scheduler.detect_cross_pet_conflicts(pet_scheduled)
            if cross_warnings:
                st.subheader("Cross-Pet Conflicts")
                for msg in cross_warnings:
                    st.warning(msg)
elif not owner_name:
    st.info("Enter your name above to generate a schedule.")
