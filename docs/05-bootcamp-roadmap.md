# Bootcamp Roadmap (1 month)

A draft sequence for the 1-month bootcamp (offline Bengaluru or live online). Each day = ~1.5–2 hours of taught content + hands-on.

## Week 1 — Foundations of data discipline

| Day | Lesson | Output |
|---|---|---|
| 1 | The Company OS vision; why trackers matter | Repo scaffold on each participant's laptop |
| 2 | The Tracker Design Bible (this document) | Master Registry sheet created |
| 3 | Tracker #1: `hr-attendance` | Working sheet + 20 rows seed data |
| 4 | Tracker #2: `mfg-daily-production` | Working sheet |
| 5 | Tracker #3: `inv-finished-goods` | Working sheet |
| 6 | Tracker #4: `sales-d2c-orders` | Working sheet |
| 7 | Tracker #5: `fin-cashflow` | Working sheet. **5 foundational trackers live.** |

## Week 2 — Operational depth + first skills

| Day | Lesson | Output |
|---|---|---|
| 8 | Setting up Claude Code; the skills folder; `CLAUDE.md` | Claude Code installed and configured |
| 9 | Google Sheets API + service account; `read_sheet.py` | Working sheet reader script |
| 10 | First atomic skill: `attendance-today` | Working skill, queryable in Claude Code |
| 11 | Atomic skills for trackers #2–#5 | 5 working atomic skills |
| 12 | Tracker #6–8: `hr-employee-master`, `qc-final`, `inv-components` | 3 more trackers |
| 13 | Atomic skills for #6–8 | 3 more skills |
| 14 | Trackers #9–11: `sales-b2b-pipeline`, `cs-tickets`, `fin-expenses` + skills | 11 trackers, 11 skills |

## Week 3 — Composite skills + advanced trackers

| Day | Lesson | Output |
|---|---|---|
| 15 | Composite skills: `morning-briefing` | Composite skill running |
| 16 | Composite skills: `weekly-review`, `board-update` | More composites |
| 17 | R&D trackers (`rnd-project-pipeline`, `rnd-bom-master`) | Advanced trackers |
| 18 | Marketing trackers + skills | More |
| 19 | Device telemetry trackers + skills | More |
| 20 | Graduate from `read_sheet.py` to Google Sheets MCP server | Cleaner integration |
| 21 | Compliance, admin, catalog trackers | Long-tail trackers |

## Week 4 — Action skills + the founder's daily flow

| Day | Lesson | Output |
|---|---|---|
| 22 | Write-back skills (`write_sheet.py`) — safety & guardrails | Action skills introduced |
| 23 | Action skill: `log-defect` | Working write skill |
| 24 | Action skill: `mark-rma-shipped`, `update-stock` | More action skills |
| 25 | Founder's morning routine: walking through a real day | Polished workflow |
| 26 | Scheduling: cron + `claude -p` for automated briefings | Automated morning brief |
| 27 | Preview of Phase 4: Slack/WhatsApp bot via Agent SDK | Conceptual closeout |
| 28 | Showcase day — each participant demos their Company OS | Graduation |

---

## Instagram content plan (parallel to bootcamp)

| Type | Count | Format |
|---|---|---|
| Tracker reveals | ~80 | Ugly sheet → beautiful sheet transformation (30–60s) |
| Atomic skill demos | ~30 | "Ask Claude how attendance is today" (15–30s) |
| Composite skill demos | ~5 | "My founder's morning briefing in 10 seconds" (45–60s) |
| Behind-the-scenes / teaching | ~20 | Schema discipline tips, design rules (30s each) |
| Founder-day montage | ~5 | Highlight reel showing a real founder using the OS |

Total: ~140 short videos across the 30-day build. Posted 3–4 per day during the build period.

## Bootcamp positioning

- **Audience**: founders and ops leaders of small Indian product / services companies (5–50 employees).
- **Promise**: in 30 days, you turn your company's chaos into a structured data-first OS with an AI assistant on top.
- **Format**: 1-month, daily 2-hour sessions; offline in Bengaluru first, online later.
- **Price**: TBD.
- **Prerequisite**: Comfort with Google Sheets, willingness to install Claude Code, a real company to model.

## What's deliberately *not* in the bootcamp

- Programming. Participants don't write Python beyond copy-pasting one reader script.
- Custom UI / app development.
- Multi-user deployment (Slack/WhatsApp). Mentioned in week 4 as a "next step" only.
- Accounting theory. We track for Claude to read; books still live in Tally.
