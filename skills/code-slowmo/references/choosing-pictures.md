# Choosing the right picture

Choose the picture by the question the reader is asking, not by what looks impressive.

## Question → section

| The reader asks | Section | Notes |
|---|---|---|
| What are the parts, and which ones talk to each other? | `map` | Start zoomed out (areas). Add a `tour` that follows one real action through the parts. |
| In what order do things happen, and who tells whom? | `flow` | One action, start to end. Add a screen mock so the reader sees the effect of each message. |
| What exactly does this function do, value by value? | `trace` | Real code, real line numbers, realistic values. At least one guess-first question. |
| What changes between approach A and approach B? | `compare` | The same scenario, stepped together, so the difference is visible. |
| What do these words mean? | `glossary` | Put it first whenever the page uses 3 or more new terms. |
| How does the output depend on an input? | `custom` | A figure the reader can drag or slide, such as a threshold or a position. |
| How is the data shaped, and what points to what? | `trace` with rich `state`, or `custom` | Show the structure before and after one change. |
| Which parts of the screen update, and why only those? | `flow` with lanes for each component, or `custom` | Light up what updates and leave the rest grey. |

## Zooming

Pages work best when they zoom in on one action:

```
glossary  →  map (tour follows the action)  →  flow (the action, message by message)  →  trace (the key function, line by line)
```

Every section should say how it connects to the one before it, for example "This zooms into step 13 above".

## When the codebase is big

Don't put the whole system on one page. Plan a series that goes from the outside in, with one question per page:
1. The system from far away (map).
2. The words you need (glossary, plus a short text section).
3. One page per important action (flow, with a short trace of its key function).
4. Deep dives for the trickiest functions (trace) and design choices (compare).

Offer the series to the user as a short list, with a one-sentence question for each page, and build the first one.

## Building a `custom` figure

Use `custom` only when no built-in section can show the idea. Good uses:
- **Drag it yourself:** the reader moves a box, and the figure shows the code's decision live. For example: "Is the pointer past the middle of this block?"
- **Slider:** the reader changes one number, like a timeout or a list length, and sees the result.
- **Before and after a data structure,** drawn as boxes and arrows.

Rules for a custom figure:
- It starts paused, in a state that already makes the point.
- Its controls sit below the figure, so a finger or cursor doesn't cover it.
- It uses role colors for the same things as the rest of the page, and yellow only for "just changed".
- Plain text sits right next to it and says what to try ("Drag the box below the middle line and watch the position change").
- It uses the page's CSS variables, so it works in dark mode.
- Its logic copies the real code's logic, and the text names the file and line it comes from.
