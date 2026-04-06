# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The following features were added to `pawpal_system.py` and `app.py` to make the scheduler more useful for real pet owners.

**Priority & time-slot sorting**
Tasks are sorted by a three-level key — priority (HIGH → LOW), then recurrence (daily before weekly before one-off), then shortest duration. Within the final scheduled list, tasks with an assigned time slot appear first in chronological order; unscheduled tasks follow.

**Age-aware priority boost**
HEALTH tasks are automatically elevated to HIGH priority for pets under age 2 or over age 8. This ensures vet visits, medications, and wellness checks are never bumped by lower-priority tasks for vulnerable pets.

**Recurring tasks**
Tasks can be marked `daily` or `weekly`. When a recurring task is checked off, a fresh copy is automatically queued for its next occurrence — no need to re-add it manually.

**Conflict detection**
The scheduler checks for overlapping time windows and reports plain-English warnings rather than crashing. Same-pet conflicts (e.g. two tasks booked at 09:00 for the same pet) and cross-pet conflicts (e.g. a walk for Buddy and a grooming for Luna scheduled at the same time) are both detected and displayed separately.

**Smarter skipping**
Tasks that exceed the entire daily budget are flagged as individually impossible and surfaced in the skipped list with a clear reason, rather than silently disappearing.

**UI improvements**
- Filter the schedule view by pet or by completion status (all / incomplete only).
- Live time-budget summary updates as tasks are added to a pet.
- Checkbox state persists across schedule regenerations.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
