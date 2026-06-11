# Company OS

A Claude Code-powered operating system for a small product company.

## What this is

A complete blueprint and working setup for running a 20-person Indian hardware company (case study: an AQI monitor maker that also resells white-label speakers) entirely on:

- **Google Sheets** as the source-of-truth data layer
- **Claude Code** as the founder's personal assistant on top of those sheets
- A library of **Skills** that compose into higher-order workflows

It is simultaneously:

1. A **working personal-OS** for one founder.
2. A **bootcamp curriculum** (1-month, offline or live online) teaching others to build their own.
3. A **content library** — one Instagram reel per tracker, per skill.

## Current scope

- **One user**: the founder.
- **One machine**: the founder's laptop.
- **One tool**: Claude Code.
- **One data backbone**: Google Sheets.

No multi-user, no Slack/WhatsApp bots, no deployed servers. Those are explicit *future* phases — out of scope for v1.

## Repo layout

```
company_os/
├── README.md
├── docs/                   # Vision, org, sources of truth, design bible, roadmap
├── trackers/               # Schemas + seed data, one folder per tracker (all domains)
│   ├── hr-*  mfg-*  inv-*  sales-*  mkt-*
├── reports/                # Unified outputs root — every skill writes generated reports here
│   ├── marketing/{daily,weekly,monthly}/
│   └── inventory/          # finished-goods.csv, stock-movement.csv, reorder-report.txt, inputs/
├── marketing/              # Marketing domain workspace (non-tracker assets)
│   ├── brand-profile.md  reporting-spec.md  HANDOFF.md
│   └── creatives/          # asset library + creatives-index.csv
└── .claude/
    └── skills/             # All Claude Code skills, one folder each (SKILL.md + scripts/ + references/)
        ├── marketing-os-setup/     # one-time setup agent
        ├── marketing-head/         # daily/weekly/monthly reports + creative housekeeping
        └── inventory-recompute/    # event-sourced stock engine
```

### Conventions (uniform across the repo)
- **Skills** live only in `.claude/skills/<name>/` (never as loose scripts).
- **Trackers** (schema + seed data) live only in `trackers/<category>-<noun>/`.
- **Generated outputs** land only under `reports/<domain>/` — never hand-edited; rebuilt each run.

## Where we are

Trackers built across HR, manufacturing, inventory, sales, and marketing. Three skills live in
`.claude/skills/`: `marketing-os-setup`, `marketing-head`, and `inventory-recompute`. All generated
reports are unified under `reports/<domain>/`.
