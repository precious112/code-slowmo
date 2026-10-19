# code-slowmo

**Understand code by watching it run in slow motion.**

https://github.com/user-attachments/assets/183da761-51d4-449c-8c34-f6bf3ba143d0

Ask your coding agent how something works and you usually get a wall of text. code-slowmo is a skill that makes your agent build an interactive page instead:

- **A system map.** It shows the main parts and which parts talk to each other. Click an area to see its parts, or follow a guided tour of one action.
- **A step-by-step timeline.** It follows one action from start to end. Each arrow is one part telling another part something. A small mock of the screen and the data change at every step.
- **A line-by-line run of the real code.** It shows the functions running, the values (yellow when they change), a log, and what you'd see on screen. A couple of steps ask you to guess what happens next before showing you.

Every sentence is short and plain. Every code name has a plain explanation you can hover. The skill includes a checker that refuses to build a page with jargon, overlong steps or unexplained code names.

The result is one HTML file. It opens in any browser and needs no server or account.

**See examples** (download a file and open it in your browser):
- [`examples/puck-drop.html`](examples/puck-drop.html) explains how the [Puck](https://github.com/puckeditor/puck) page editor handles a drag-and-drop, from the system map down to the one line that adds the block.
- [`examples/puck-undo.html`](examples/puck-undo.html) explains how undo works in Puck. A fresh agent made it from one question, using only this skill.

## Install

**Claude Code**
```
/plugin marketplace add precious112/code-slowmo
/plugin install code-slowmo@code-slowmo
```

**Codex, Cursor and other agents that support skills**
```
npx skills add precious112/code-slowmo
```

**OpenCode**

Install it for one project (run this in the project folder):
```
npx skills add precious112/code-slowmo -a opencode
```
Or install it for every project:
```
npx skills add precious112/code-slowmo -a opencode -g
```
OpenCode finds the skill on its own. Ask a question about your code, or type `/code-slowmo`. If your `opencode.json` limits skills with `permission.skill`, allow `code-slowmo` there.

To install without npx, copy `skills/code-slowmo/` to `.opencode/skills/code-slowmo/` in your project, or to `~/.config/opencode/skills/code-slowmo/` for every project.

**By hand, for any agent:** copy `skills/code-slowmo/` into your agent's skills folder. For Claude Code that is `~/.claude/skills/`.

You need Python 3.8 or newer, which the agent uses to build the page.

## Use

Ask a question about how code works, in your own words:

- "How does undo work in this editor? What happens when I press it?"
- "Walk me through what happens when a user signs up."
- "I'm new to this repo. Give me the big picture."
- "What exactly does `reconcileChildren` do, line by line?"

The agent reads the code, writes the page and saves it to `explainers/` in your project. You can also call the skill by name. In Claude Code, run `/code-slowmo`, or `/code-slowmo:code-slowmo` if you installed it as a plugin.

## How it works

1. The agent reads the real code first and notes the file and line behind each claim.
2. It writes the page content as a small JSON file: the question, the parts, the steps and the explanations.
3. `scripts/build.py` checks that file. It catches structure mistakes and writing problems, such as steps over 40 words, code names with no plain explanation, filler words and passive voice. Then it builds the page from one shared template.
4. You get one self-contained HTML file. The JSON stays next to it, so you can ask for changes and rebuild.

The design follows research on learning from pictures and animation. Pages start paused, you control the pace, the layout never jumps around, and you're asked to predict before key moments. The principles and their sources are in [`skills/code-slowmo/references/design-principles.md`](skills/code-slowmo/references/design-principles.md).

## What's inside

```
skills/code-slowmo/
├── SKILL.md                    the instructions the agent follows
├── references/
│   ├── writing.md              the plain-writing rules (the most important file)
│   ├── page-format.md          every field of the page data
│   ├── choosing-pictures.md    which picture answers which question
│   └── design-principles.md    why the pages behave the way they do
├── scripts/
│   ├── build.py                checks the page data and builds the HTML
│   └── check_text.py           the plain-writing checker
└── assets/
    ├── template.html           the page engine
    └── examples/puck-drop.json a complete example page
```

## License

MIT
