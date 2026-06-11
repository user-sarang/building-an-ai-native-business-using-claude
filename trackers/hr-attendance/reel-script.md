# `hr-attendance` — Instagram reel script

Format: 45–60s vertical reel. Voiceover + screen recording.

## Hook (0–3s)
Visual: A messy attendance sheet — typos, mixed date formats, no colors. Camera shake/zoom for chaos effect.
VO: *"This is what 90% of Indian companies use to track attendance. Watch this."*

## Setup (3–10s)
Visual: Quick whip-pan to a blank Google Sheet.
VO: *"In 5 minutes, I'll show you the attendance tracker your founder will actually open every morning."*

Text overlay: **HR-ATTENDANCE  ·  Day 3 of 30**

## The build (10–35s)
Quick cuts, each 2–3 seconds, with text labels:

1. **"Stable IDs"** — type `ATT-20260601-001` in column A
2. **"ISO dates"** — type `2026-06-01` in column B
3. **"Dropdown statuses"** — click Data Validation → paste enum list → flash the dropdown
4. **"Pill formatting"** — paste conditional formatting rules → click through statuses, watch them light up green/red/amber
5. **"Computed hours"** — paste `=check_out-check_in` formula → number appears
6. **"Late minutes"** — paste `=MAX(0, check_in - TIME(9,30,0))*1440` → numbers pop
7. **"Frozen header + zebra stripes"** — apply formatting → scroll demo
8. **"Dashboard tab"** — switch tabs → 3 big KPI cards already there: PRESENT TODAY 18, ATTENDANCE % 90%, LATE 3
9. **"Chart"** — drop in a 30-day line chart

## The reveal (35–45s)
Visual: Side-by-side. Old ugly sheet vs new sheet.
VO: *"Same data. Different decade."*

## The Claude moment (45–55s)
Visual: Terminal opens. Type `claude` → ask: *"How is attendance today?"*
Output appears on screen: the formatted summary from `claude-tips.md`.
VO: *"And once it looks like this — your AI assistant can actually read it."*

## CTA (55–60s)
Text overlay: **30 trackers · 30 days · 1 bootcamp**
*"Link in bio if you want to build this for your company."*

## Captions / hashtags

Caption draft:
> Day 3 — HR Attendance.
> The 4 rules that turn a chaos sheet into a tracker your founder actually opens:
> 1. Stable IDs (never reuse)
> 2. ISO dates (`YYYY-MM-DD`)
> 3. Enums via dropdowns
> 4. Conditional-formatted status pills
> Once your data is clean, Claude can read it.
> Full 80-tracker series → bootcamp link in bio.

Hashtags: `#googlesheets #foundertools #buildinpublic #indianstartup #operations #productivity #aitools #claudeai`

## B-roll list
- Close-up of dropdown opening (slow-mo)
- Cursor hovering over status, pill changes color
- Tab switch animation
- Founder/protagonist on laptop (over-the-shoulder)
- Terminal typing the question to Claude
- Claude's structured response appearing line by line

## Music
Upbeat lo-fi or minimalist build-up track. Snap on each cut.
