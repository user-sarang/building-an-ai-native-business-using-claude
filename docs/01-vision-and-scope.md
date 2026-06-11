# Vision & Scope

## The case-study company

A 20-person Indian hardware company that:

- **Manufactures** desktop AQI (Air Quality Index) monitors in-house.
- **Resells** white-label Bluetooth speakers (sources finished product, brands it, sells it).
- Has an in-house **R&D** team working on next-generation products.
- Sells **D2C** (Shopify + Amazon India) and **B2B** (corporates, schools, hospitals).
- Operates entirely in India: Tally/Zoho for accounting, Razorpay for payments, WhatsApp Business for support, Shiprocket for logistics, Google Sheets for everything else.

## The vision

Every function of the company captures data in a well-designed Google Sheet. Claude Code, running on the founder's laptop, reads these sheets and answers natural-language questions like:

- "How is attendance today?"
- "What's our cash position?"
- "Which AQI batch had the highest defect rate this week?"
- "Give me the morning briefing."

These are implemented as **Skills** — small markdown specs Claude Code loads on demand. Atomic skills (one tracker each) compose into higher-order skills (`morning-briefing`, `weekly-review`, `board-update`).

The end-state is a **personal assistant for the founder** that pulls live data from across the company on demand.

## Phasing

| Phase | Scope | Users |
|---|---|---|
| **1. Build skills locally (current)** | Founder uses Claude Code on laptop, skills folder + Google Sheets | 1 (founder) |
| 2. Daily use, polished | Same setup, automated morning briefings via cron, WhatsApp delivery | 1 |
| 3. Headless / scheduled | `claude -p` runs key skills on a schedule | 1 |
| 4. Team access (future, out of scope) | Slack/WhatsApp bot via Claude Agent SDK reusing same skills folder | 20 |

Phases 2-4 are *future work*. This repo focuses on Phase 1.

## Triple purpose

This project produces three deliverables in parallel:

1. **A working setup** for one real founder.
2. **A bootcamp curriculum** (1-month, offline Bengaluru or live online) that teaches participants to replicate it for their own companies. Tracker design + Claude Code skills.
3. **An Instagram content library** — one short reel per tracker (~80) and per skill (~30+), showing the visual transformation of messy sheets into well-designed ones and the "wow moment" of chatting with Claude over live company data.

## Why this is teachable

Most small companies operate on a chaos of WhatsApp messages, ad-hoc spreadsheets, and tribal knowledge. The two unlocks taught here:

1. **Data discipline** — well-designed trackers with schemas, validation, and visual hierarchy.
2. **Agentic access** — Claude Code as the conversational layer over those trackers.

Each unlock alone is valuable. Together they are a step-change in how a small company operates.

## Non-goals (explicit)

- Not building custom software, mobile apps, or web dashboards.
- Not building a SaaS product.
- Not replacing Tally / Shopify / WhatsApp.
- Not multi-user in v1.
- Not handling PII at scale (employee data stays in the founder's Google Workspace).
