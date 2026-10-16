# Writing for code-slowmo pages

The reader is smart but new to this code. They came here because a long technical answer lost them. Every sentence on the page is either something they can follow or a reason to close the tab.

These rules apply to every piece of reader-facing text: titles, the question, intros, glossary meanings, part explanations, arrow labels, step text, questions, answers, log lines and the takeaway.

## Contents
1. The rules
2. The "who does what, when" test
3. Explaining code names and technical words
4. Writing each kind of text
5. Before and after
6. Words and patterns to avoid
7. Final check

## 1. The rules

1. **Say the point first.** Open with what happens or what matters. Background comes after, if at all.
2. **One idea per sentence.** Aim for 15 to 20 words. Split any sentence over 25.
3. **Keep a step under 40 words.** If it needs more, it is two steps.
4. **Use active voice, and name who acts.** "The store saves the block", not "the block is saved".
5. **Use everyday words.** "Use" not "utilize", "start" not "initialize", "send" not "dispatch", "show" not "render", unless you are naming the code.
6. **Name things the way the reader sees them.** Use the button, screen or feature name ("the drop line", "the Fields panel"), not the code name (`LinePlaceholder`). Show the code name once, as a secondary label, so the reader can find it in the repo.
7. **Explain every code name and technical word where it first appears**, or leave it out (section 3).
8. **Don't invent labels.** Don't coin shorthand ("the commit seam", "the wire state") and then use it as if the reader knows it. If something needs a name, first say what it is in a full sentence.
9. **Be concrete.** Use a real example from this code ("you drop it between Hero and Text, so the position is 1"), not an abstract one ("the computed insertion index").
10. **Simplify the language, never the substance.** Keep the precise detail. Explain it plainly instead of leaving it out.

## 2. The "who does what, when" test

Read every sentence and ask three things:
- **Who** does the action? Name the actor.
- **What** exactly happens? Name the visible or concrete change.
- **When** does it happen? On every pointer move? Once, after the drop?

If any answer is missing or vague, rewrite the sentence. Vague sentences usually look like these:
- "Its drops end in the same code that moves blocks." *Whose drops? What code? When?*
- "This handles the update." *What is "this"? Which update?*
- "The data flows through to the view." *What data? Who sends it? What does the view do?*

A real example from building this skill. The first version said:
> A tree view of your page. You can drag blocks here too. Its drops end in the same code that moves blocks on the canvas.

The reader couldn't tell what "its drops" meant. The fix says what happens in order:
> A list of every block on your page, in the left sidebar. You can drag a block to a new spot in this list. When you let go, Puck moves the block on the page too. It uses the same function as when you drag a block on the canvas.

## 3. Explaining code names and technical words

- **Code names in the text go in `<code>…</code>`, and each one needs an entry in `terms`.** The entry is one plain sentence saying what it is or does. Readers see it when they hover the name. The build fails if an entry is missing.
  - `"insertComponent": "Puck's function that adds a new block to the page."`
  - `"root:default-zone": "Puck's name for the page's main list of blocks."`
- **Still explain the name in the sentence when it matters to the step.** The tooltip is a backup, not a replacement. Write "Puck calls `insertComponent`, which adds the new block", not just "Puck calls `insertComponent`".
- **Technical words** like store, action, iframe, callback, render or reducer: explain each one in a glossary card, or in the sentence the first time ("an iframe, a page inside the page"), or swap it for a plain word ("redraw" instead of "re-render").
- **Use fewer code names.** If the reader doesn't need the name to follow the step, describe what the code does instead.
- **Real values** like `"root:default-zone"` count as code names. Explain what the value means.

## 4. Writing each kind of text

- **Title:** a short name for the page ("How a drop works in Puck"). No colon followed by an explanation.
- **Question:** the one question the page answers, in the reader's words.
- **Intro:** two or three sentences. Say what the page follows and how it is laid out.
- **Glossary meaning:** what the thing is, then what it does, then an example. Two or three sentences.
- **Part `about` (map):** what the part does and when, in two or three sentences. Don't list its internals.
- **Arrow labels and timeline labels:** two to five words, saying what is sent or asked ("preview to draw", "add Heading at position 1"). Never just "calls" or "uses".
- **Step `say`:** what happens on this step and why it matters, under 40 words. On a code line, say what the line does in plain words, then what that means for the reader ("Nothing has changed on screen yet").
- **Guess-first question (`ask`):** ask just before the surprising moment. Make every wrong option tempting, not silly. In `why`, start with the answer, then explain.
- **Log lines:** past tense, plain: "Saved an undo step." "Main drop area redrew."
- **Takeaway:** one or two sentences the reader should remember tomorrow.

## 5. Before and after

| Before | After |
|---|---|
| The DropZone subscribes to the zone-scoped slice of the preview index via a selector, triggering reconciliation. | Each drop area watches one thing: the preview for itself. When that changes, it redraws. |
| Note that the data is immutably updated. | Puck never edits the old list. It makes a new copy, so React can tell something changed. |
| `insertedState` is computed eagerly to avoid a race with resolveData. | Puck builds `insertedState` now, so it can look up the new block without waiting for the store. |
| On drag end the commit is deferred until the source becomes idle. | When you let go, Puck waits for the block to finish gliding into place. Then it saves the change. |
| The reducer handles the action. | The store runs its reducer, the function that turns "add a Heading at position 1" into new page data. |
| Silent clamping at the boundary. | You type 22px, and it saves 20px. |

## 6. Words and patterns to avoid

The checker flags most of these.
- **Filler and inflated words:** utilize, leverage, facilitate, seamless, robust, delve, orchestrate, powerful, elegant, magic, "under the hood", "plays a key role", "it's worth noting", "note that", "in order to".
- **Softeners that add nothing:** simply, just, basically, essentially, obviously, clearly, actually.
- **Em dashes:** an aside set off by dashes is usually a second sentence. Write two sentences.
- **"Not X, but Y" setups, and colon-then-reveal:** say Y directly.
- **Scare quotes around made-up labels.**
- **Vague subjects at the start of a sentence:** "It", "This", "That" when the reader can't tell what they point to.
- **Passive voice** that hides who acts.

## What the checker flags

`scripts/check_text.py` holds the exact word lists. In short:
- **Errors (the build stops):** a step over 45 words, a sentence over 32 words, `<code>` with no `terms` entry, filler words, and "Note that".
- **Warnings:** a step over 40 words, a sentence over 24 words, softeners, possibly unfamiliar technical words (like handler, dispatch, callback, iframe) that aren't explained nearby or in the glossary, passive voice, em dashes, labels over 6 words, and sentences that open with "It is", "This does", "That means" and similar, where the reader can't tell what "it" is.

A technical word counts as explained if it appears in the glossary, `terms`, a map part name, a lane name or a role name. It also counts if the same sentence explains it, like "an iframe (a page inside the page)".

## 7. Final check

Before building, read every step as if you had never seen the code:
- Is the point in the first sentence?
- Does every sentence pass the "who does what, when" test?
- Is every code name, file name and technical word explained, or replaced with a plain word?
- Did you invent any label? Replace it with what it is.
- Can any sentence be shorter and still say the same thing?
- Is every "never", "always", "only" or "every" true on every platform and every code path? Check it in the code, or soften it ("on macOS and Linux…").
- Do the numbers you state ("six areas", "ten steps") match what is on the page? The build warns when they don't.
- Do you only tell the reader to press buttons that exist? See page-format.md, section 5.

If any answer is "no", rewrite before you build.
