# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.

     There are 5 main classes outlined in the UML design that form the skeleton of the pet care app. They have relations with each other and one is dependent on the other to generate an output for the application. The five main classes are Pet, Owner, Task, Scheduler, and Daily plan.


- What classes did you include, and what responsibilities did you assign to each?

    The initial UML design includes the classes Pet, Task, Owner, Scheduler, and Daily plan. The Tasks class stores information about tasks that need to be done. The Pet class stores information about the pets. The owner class includes data such as best time for getting pet cleaned. The scheduler class generates the Daily Plan class and its the main backbone of the app. The Dailyplan app is generally the output and the vehicle for the data to display to the end user.

**b. Design changes**

- Did your design change during implementation?

    Yes

- If yes, describe at least one change and why you made it.

    The scheduler had to be changed to better accomodate the decision to include which tasks to the scedule. Decided whether priority of tasks or number of tasks should be completed saw some design system from the original flow of the scheduler class.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

    The constraints the scheduluer considers is time and priority of tasks

- How did you decide which constraints mattered most?

    I deciced to first consider the constraint of priority first then time as secondary to that.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

    It trades off completing tasks that are high priority than completing more tasks

- Why is that tradeoff reasonable for this scenario?

    I felt that this would be prefered by more pet owners as tasks such as feeding pets holds more importance than maybe grooming as feeding is something critical to a pet's survival
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

    I used AI to help me brainstorm, refactor, and make tests

- What kinds of prompts or questions were most helpful?

    The prompts that were more specific were most helpful. For example, the prompts that detailed specific changes and behaviors that I wanted the app to have, helped using the agent mode go more smoothly and decreased the amount of prompting I had to do.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

    There was a AI suggestion where the AI wanted to change many different methods in scheduler when I was trying to implement the recurring task feature. I didn't accept it because it was adding redundant functions that made the code bloated.

- How did you evaluate or verify what the AI suggested?

    I evaluated the AI suggestion by asking it what the change would do to the code and if it was an optimized change.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

    I tested behaviors for every feature of the app to make sure they worked as intended.

- Why were these tests important?

    These tests were important because the app needs to work as designed without unintended glitches and behaviors. Also every new feature had to be tested to not impact other features.

**b. Confidence**

- How confident are you that your scheduler works correctly?

    I'm fairly confident that the scheduler works as intended.

- What edge cases would you test next if you had more time?

    I want to test the edge cases that involve multiple pets having similar tasks and are of equal priority that is occuring at the same time.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

    I'm most satisfied with the testing suite. I felt that it effectively tested the app for intended behavior and caught some uninteded behaviors that I initially didn't catch when I allowed the AI to first implemnt a new feature.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

    I would redesign the UI to be more intuitive and efficient. As a user, the UI feels too basic and more features could be implemented to make filling out certain data more streamlined.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

    I learned how in systems many things are interconnected and when you change one part, you have to ensure others parts of the system isn't affected. This was especially clear when trying to refactor or introduce new features. Often times other parts of the system had to be redesigned or refactor to make everything work again.
