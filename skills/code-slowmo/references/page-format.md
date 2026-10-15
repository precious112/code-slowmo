# Page data format

A page is one JSON file. `scripts/build.py page.json page.html` checks it and builds the HTML.
[assets/examples/puck-drop.json](../assets/examples/puck-drop.json) uses every common feature, so start from a copy of it.

## Contents
1. Top level
2. Text you can format
3. Sections: glossary, text, map, flow, trace, compare, custom
4. Screens and state
5. Links to a step

## 1. Top level

| Field | Required | What it is |
|---|---|---|
| `title` | yes | Short page name. Also the browser tab title. |
| `question` | yes | The one question this page answers. |
| `takeaway` | yes | One or two sentences to remember. Shown at the end. |
| `intro` | no | A paragraph, or a list of paragraphs, under the question. |
| `eyebrow` | no | Small line above the title, such as the repo name. |
| `subject` | no | What the page describes: project, version, folder, commit. |
| `roles` | no | Up to 5 color groups: `[{ "id", "name", "about" }]`. Colors go amber, violet, blue, green, rose, in order. |
| `terms` | yes, if any `<code>` is used | `{ "codeName": "plain one-sentence explanation" }`. Readers see it on hover. |
| `sections` | yes | The list of sections, in reading order. |
| `footer` | no | A small note at the bottom. |

## 2. Text you can format

**Code names and `terms`:** the page matches each `<code>` text to `terms` exactly. Only put a name in `<code>` when the reader needs it, for example to find it in the repo. For a plain local variable like `state`, describe it in words instead ("the current page data").


All reader-facing text accepts a small set of HTML:
- `<b>…</b>` to emphasise the key fact of a step. Use it at most once per step.
- `<i>…</i>` for placeholders, like *owner*:*list*.
- `<code>…</code>` for code names and real values. Each one needs a `terms` entry (see writing.md, section 3).
- `<span class="role" data-role="ROLE_ID">…</span>` colors a word with a role's color.
- `<span class="example">example</span>` tags a made-up value.

Don't use other HTML in text fields. Screens (section 4) and `custom` sections can use any HTML.

## 3. Sections

Every section has `type` and can have `id` (used in links; default: type plus position), `title`, `eyebrow` and `intro`. A page can have several sections of the same type, such as two traces. Give each one its own `id`.

### glossary
`items`: `[{ "word", "code"?, "meaning", "example"?, "role"? }]`. Use 3 to 7 cards. `word` is the plain name. `code` is the name in the code.

### text
`body`: a paragraph or a list of paragraphs. Use it for short bridges between sections, not for long explanations.

### map
Draws areas holding parts, with links between them. The page lays it out automatically. You choose the rows.

| Field | What it is |
|---|---|
| `areas` | `[{ "id", "name", "about", "span"? , "cols"? }]`. An area is a region of the system. `span` is its relative width in its row (default 1). `cols` is how many columns its parts use. |
| `rows` | A list of rows, each a list of area ids, top to bottom: `[["ui"],["api","worker"],["db"]]`. Put parts that talk most in neighbouring rows. Default: 3 areas per row, in order. |
| `parts` | `[{ "id", "area", "name", "about", "role"?, "code"?, "file"?, "sub"? }]`. `name` is the plain name. `code` is the code name, shown small under it. `file` is `path:line`. `sub` replaces the small line under the name. |
| `links` | `[{ "id", "from", "to", "label", "role"?, "both"? }]`. An arrow between two parts. `label` is 2 to 5 words. Give every link an `id` if the tour uses it. |
| `areaLinks` | Optional arrows for the zoomed-out view: `[{ "from", "to", "label", "both"? }]` between area ids. If you leave it out, the page draws one unlabelled arrow for each pair of areas that have links between their parts. |
| `start` | `{ "title", "body" }`: the side panel shown before any click. Use it for the one key idea. |
| `tour` | `[{ "say", "parts"?, "links"?, "tick"? }]`. Each tour step lights up those parts and links. A step with no parts shows the zoomed-out view. |
| `note` | A small label in the corner, like the folder the map covers. |

Keep it to 5 to 12 parts and 4 to 6 areas. If there are more, make a second map page.

### flow
A timeline: lanes across the top, messages going down in time order.

| Field | What it is |
|---|---|
| `lanes` | `[{ "id", "name", "role" }]`. Use 3 to 7 lanes, with short names of 12 characters or fewer. |
| `steps` | `[{ "from", "to", "label", "say", "phase"?, "tick"?, "screen"?, "state"? }]`. `from` equal to `to` draws a loop (something that happens inside one part). `phase` draws a divider with a short word of your choice ("drag", "drop", "undo") before the step. `tick` puts a labelled mark on the step bar. |
| `screenLabel`, `stateLabel` | Optional headings for the screen and data panels. |

Aim for 8 to 16 steps. Each step is one message. If two things happen at once, use two steps.

### trace
Real code, one line at a time.

| Field | What it is |
|---|---|
| `files` | `{ "key": { "path", "start", "code" } }`. `code` is copied exactly from the file. `start` is the real line number of its first line. Include just the functions you step through. The page removes shared leading indentation for display, but line numbers stay real. Set `"dedent": false` to turn that off. |
| `frames` | `{ "key": { "name", "about", "role" } }`. Each function that appears in the "functions running now" panel. `about` is 2 to 6 plain words, like "adds a new block". |
| `steps` | See the next table. |
| `screenLabel`, `stateLabel` | Optional headings for the screen and data panels. |

Each step:

| Field | What it is |
|---|---|
| `file`, `line` | Which file and real line number is running. |
| `to` | Optional last line, to highlight a range (a multi-line call or object). The explanation box appears under the last highlighted line. |
| `stack` | The running functions, outermost first: `["handler", "insertComponent"]` (keys into `frames`). Use the real function names, in the real calling order. You may skip small in-between helpers that don't matter to the story. |
| `vars` | `{ "name": "value as a reader would read it" }`: the values in the current function, after this line runs. The page turns a value yellow when it changes since the last step in the same function. |
| `say` | What the line does and why it matters. Under 40 words. |
| `ask` | Optional guess-first question: `{ "q", "options": [...], "answer": index, "why" }`. It shows under this step's explanation, before the reader presses Next. Put it on the step just before the line that reveals the answer. |
| `log` | Optional new log lines: `[{ "role", "text" }]`. Lines build up over the steps. |
| `screen`, `state` | Optional. See section 4. |
| `tick` | Optional label for a mark on the step bar. Use it for 3 to 6 key moments. |

Tips:
- Step into a called function by switching `file` and adding a frame to `stack`. Step back out by removing it.
- Skip boring lines. Every step should teach something.
- Show the moment the screen changes in the same step where the code causes it.

### compare
Two ways of doing something, stepped together.

| Field | What it is |
|---|---|
| `left`, `right` | `{ "title", "role"? }` |
| `steps` | `[{ "left": { "say", "screen"?, "state"? }, "right": { … }, "tick"? }]` |

### custom
For a figure no other section can draw, like a box the reader drags to see how a collision check decides.

| Field | What it is |
|---|---|
| `html` | Markup for the figure. Use the page's CSS variables (section 4) so it works in light and dark themes. |
| `script` | Optional JavaScript. It runs as a function of `(root, helpers)`. `root` is the figure's container. `helpers` holds `el`, `esc`, `prose`, `makePlayer`, `rc` (role color), `rbg`, `roleStyle` and `stateHTML`. |
| `frame` | Set it to `false` to drop the bordered frame. |

Read design-principles.md before writing one. It must start paused, make sense before any click, and keep plain text beside it.

## 4. Screens and state

`screen` is a small HTML mock of what the user would see at that step: the app's UI, a terminal, a file on disk, a network request. Keep it small and simple. These helper classes are available:

| Class | Use |
|---|---|
| `scr-row` / `scr-col` | Lay pieces side by side or stacked. |
| `scr-box` | A bordered block, like a button, card or list item. |
| `scr-tag` | A tiny grey label. |
| `scr-muted` | Grey text. |
| `scr-hot` | The yellow "just changed" highlight. |
| `scr-sel` | A blue selection outline. |
| `scr-ghost` | Faded and dashed, for a dragged or pending item. |
| `scr-line` | A thin blue line, like a drop position. |
| `scr-off` | A greyed-out, disabled control. |

Colors available as CSS variables: `--ink`, `--muted`, `--line`, `--surface`, `--surface-2`, `--hot`, `--r1` to `--r5` (role colors in `roles` order), and `--r1-bg` to `--r5-bg`.

`state` is a flat object of the data that matters at this step: `{ "page data · order": "Hero-1, Text-2", "drag store · preview": "none" }`. Prefix keys with where the data lives. The page highlights changed values on its own.

Both `screen` and `state` carry forward: a step without them shows the last ones given. Include them only on steps where something changes.

The page highlights changed `state` values on its own. You can also add `scr-hot` to the part of a screen that just changed.

## 5. Links to a step

Every stepped section can be linked to: `page.html#<section-id>-<step number>`, such as `#trace-14`. The reader's position updates the address as they step, so they can share the exact step.
