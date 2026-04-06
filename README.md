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

## Features

- **Greedy task scheduler** — fits tasks into the owner's daily time budget using a greedy algorithm: tasks are evaluated in priority order and added to the plan if they fit in the remaining minutes. Skipping one task never blocks a later, shorter task from being scheduled.

- **Three-level priority sort** — `sort_by_priority` orders tasks by a composite key: priority tier (HIGH → MEDIUM → LOW), then recurrence type (DAILY → WEEKLY → NONE, so routine care is never bumped by one-off tasks of equal priority), then duration ascending (shortest-first as a bin-packing heuristic to maximize how many tasks fit).

- **Chronological schedule output** — after greedy selection, `generate_plan` re-sorts the scheduled list so timed tasks appear in ascending `time_slot` order (minutes from midnight), with unscheduled tasks grouped at the end.

- **Age-aware priority boost** — `apply_age_boost` scans all tasks before scheduling and shallow-copies any HEALTH task that is not already HIGH priority when the pet's age is outside the 2–8 range (under 2 or over 8). Original task objects are never mutated.

- **Recurring task queue** — tasks carry a `Recurrence` field (NONE / DAILY / WEEKLY). Calling `mark_complete()` on a recurring task sets it to completed and returns a shallow copy with `completed=False`, ready to be appended as the next occurrence. Non-recurring tasks return `None`.

- **Impossible-task filtering** — `filter_by_time` separates tasks whose duration alone exceeds the entire daily budget before the greedy loop runs, so they are always reported in the skipped list with a clear reason rather than silently competing for time.

- **Overlap conflict detection** — `detect_conflicts` performs an O(n²) pairwise scan of all timed tasks and flags any pair where the intervals overlap using strict inequality (`a.start < b.end and b.start < a.end`). Back-to-back tasks are intentionally not flagged. Unscheduled tasks (no `time_slot`) are skipped.

- **Cross-pet conflict detection** — `detect_cross_pet_conflicts` (static method) applies the same overlap check across tasks belonging to different pets, useful when one owner manages multiple animals on the same schedule.

---

## Testing PawPal+

### Running the tests

```bash
python -m pytest tests/tests_pawpal.py -v
```

### What the tests cover

**Sorting correctness** — verifies that `sort_by_priority` orders tasks HIGH → MEDIUM → LOW, uses recurrence (DAILY → WEEKLY → NONE) as a tie-breaker, and prefers shorter tasks when priority and recurrence match. Also confirms `generate_plan` returns the final scheduled list in chronological `time_slot` order, with unscheduled tasks trailing timed ones.

**Recurrence logic** — confirms that marking a `DAILY` or `WEEKLY` task complete returns a new, distinct task object with `completed=False` and the same title/duration. Verifies that completing a task twice produces two independent occurrences, and that non-recurring (`NONE`) tasks return `None` on completion.

**Conflict detection** — checks that the scheduler flags overlapping time windows (including two tasks at the exact same slot), does not flag back-to-back tasks, and ignores unscheduled tasks entirely. Includes an end-to-end test that confirms `plan.conflicts` is populated by `generate_plan`, and cross-pet conflict tests for both the overlapping and non-overlapping cases.

### Confidence level

★★★★☆ (4/5)

32 tests pass across all three areas, covering the critical scheduling paths and all identified boundary conditions. The main gap is the UI layer in `app.py` — specifically the duplicate-occurrence guard and checkbox state — which is not covered by unit tests. Integration or end-to-end tests for the Streamlit front-end would be needed to reach full confidence.

---

## Getting started

## DEMO

 <a href="screenshots/Screenshot 2026-04-06 at 12.32.31 AM.png" target="_blank"><img src='screenshots/Screenshot 2026-04-06 at 12.32.31 AM.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>. 


 <a href="screenshots/Screenshot 2026-04-06 at 12.33.18 AM.png" target="_blank"><img src='screenshots/Screenshot 2026-04-06 at 12.33.18 AM.png' title='PawPal App' width='' alt='PawPal App' class='center-block' /></a>. 

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
