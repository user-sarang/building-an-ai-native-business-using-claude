"""
One-time generator for realistic month-of-attendance sample data.

This script produces `sample-data-month.csv` covering all working days of
May 2026 for the 20-person company, plus the existing June 1 (today) snapshot.

NOT a production component. The actual hr-attendance sheet is filled manually,
one day at a time, by HR-admin. This script only exists so the seed data
is reproducible and the patterns are documented.

Run with:
    python3 generate-sample-data.py > ../sample-data-month.csv
"""

import csv
import sys
import random
from datetime import date, timedelta

random.seed(42)  # reproducible

# Employee personas. Each has a "typical" location and a few behavioural
# tendencies. The generator uses these to make the data look believable.
EMPLOYEES = [
    {"id": "EMP-001", "name": "Arjun Mehta",     "loc": "OFFICE",  "wfh_pct": 0.10, "punctual": 0.9},  # Founder
    {"id": "EMP-002", "name": "Priya Sharma",    "loc": "OFFICE",  "wfh_pct": 0.10, "punctual": 0.85}, # COO
    {"id": "EMP-003", "name": "Rohan Iyer",      "loc": "WFH",     "wfh_pct": 0.60, "punctual": 0.6},  # Firmware
    {"id": "EMP-004", "name": "Neha Reddy",      "loc": "OFFICE",  "wfh_pct": 0.30, "punctual": 0.8},  # Hardware
    {"id": "EMP-005", "name": "Vikram Singh",    "loc": "FACTORY", "wfh_pct": 0.00, "punctual": 0.95}, # Production lead
    {"id": "EMP-006", "name": "Kavya Nair",      "loc": "FACTORY", "wfh_pct": 0.00, "punctual": 0.85}, # Operator
    {"id": "EMP-007", "name": "Aditya Krishnan", "loc": "FACTORY", "wfh_pct": 0.00, "punctual": 0.9},  # Operator
    {"id": "EMP-008", "name": "Sneha Patil",     "loc": "FACTORY", "wfh_pct": 0.00, "punctual": 0.85}, # Operator
    {"id": "EMP-009", "name": "Karthik Rao",     "loc": "FACTORY", "wfh_pct": 0.00, "punctual": 0.8},  # Operator
    {"id": "EMP-010", "name": "Meera Joshi",     "loc": "FACTORY", "wfh_pct": 0.05, "punctual": 0.7},  # QC
    {"id": "EMP-011", "name": "Suresh Babu",     "loc": "OFFICE",  "wfh_pct": 0.10, "punctual": 0.75}, # Procurement
    {"id": "EMP-012", "name": "Ananya Gupta",    "loc": "FACTORY", "wfh_pct": 0.00, "punctual": 0.4},  # Warehouse — unreliable
    {"id": "EMP-013", "name": "Rahul Verma",     "loc": "FIELD",   "wfh_pct": 0.05, "punctual": 0.9},  # B2B sales — field heavy
    {"id": "EMP-014", "name": "Divya Menon",     "loc": "OFFICE",  "wfh_pct": 0.20, "punctual": 0.85}, # D2C lead
    {"id": "EMP-015", "name": "Manish Kumar",    "loc": "OFFICE",  "wfh_pct": 0.10, "punctual": 0.5},  # Inside sales — often late
    {"id": "EMP-016", "name": "Pooja Desai",     "loc": "WFH",     "wfh_pct": 0.70, "punctual": 0.4},  # Content — late & WFH
    {"id": "EMP-017", "name": "Sandeep Bhat",    "loc": "OFFICE",  "wfh_pct": 0.15, "punctual": 0.9},  # Perf mkt
    {"id": "EMP-018", "name": "Lakshmi Pillai",  "loc": "OFFICE",  "wfh_pct": 0.10, "punctual": 0.95}, # Support
    {"id": "EMP-019", "name": "Harish Naidu",    "loc": "OFFICE",  "wfh_pct": 0.05, "punctual": 0.95}, # HR
    {"id": "EMP-020", "name": "Ritu Aggarwal",   "loc": "OFFICE",  "wfh_pct": 0.10, "punctual": 0.9},  # Finance
]

# Public holidays in May 2026 (India)
HOLIDAYS = {
    date(2026, 5, 1),   # Labour Day
    date(2026, 5, 12),  # Hypothetical state holiday (placeholder)
}

# Hand-crafted "events" per employee — concrete leave/absent stretches that
# make the data tell a story. The generator respects these first, then fills
# in normal patterns around them.
EMPLOYEE_EVENTS = {
    "EMP-001": [(date(2026, 5, 18), "LEAVE", "Investor offsite Mumbai")],
    "EMP-003": [(date(2026, 5, 6), "LEAVE", "Personal"),
                (date(2026, 5, 7), "LEAVE", "Personal")],
    "EMP-004": [(date(2026, 5, 22), "LEAVE", "Wedding in family")],
    "EMP-005": [(date(2026, 5, 13), "LEAVE", "Sick — fever")],
    "EMP-008": [(date(2026, 5, 14), "HALF_DAY", "Hospital — mother appointment"),
                (date(2026, 5, 15), "LEAVE", "Hospital — mother appointment")],
    "EMP-010": [(date(2026, 5, 25), "HALF_DAY", "Personal work afternoon")],
    "EMP-011": [(date(2026, 5, 11), "LEAVE", "School admission for son")],
    "EMP-012": [(date(2026, 5, 5), "ABSENT", "No call no show"),
                (date(2026, 5, 6), "ABSENT", "No call no show"),
                (date(2026, 5, 7), "LEAVE", "Apologised — family emergency"),
                (date(2026, 5, 19), "ABSENT", "No call no show — repeated issue")],
    "EMP-013": [(date(2026, 5, 4),  "PRESENT", "Site visit - Wipro Sarjapur"),
                (date(2026, 5, 8),  "PRESENT", "Site visit - Manyata Tech Park demo"),
                (date(2026, 5, 14), "PRESENT", "Site visit - Embassy GolfLinks"),
                (date(2026, 5, 21), "PRESENT", "Site visit - NIMHANS proposal"),
                (date(2026, 5, 27), "PRESENT", "Site visit - DPS school AQI demo"),
                (date(2026, 5, 28), "PRESENT", "Site visit - Inventra Tech Park")],
    "EMP-015": [(date(2026, 5, 20), "HALF_DAY", "Bike service")],
    "EMP-016": [(date(2026, 5, 26), "LEAVE", "Personal")],
    "EMP-017": [(date(2026, 5, 6),  "LEAVE", "Brother's wedding"),
                (date(2026, 5, 7),  "LEAVE", "Brother's wedding"),
                (date(2026, 5, 8),  "LEAVE", "Brother's wedding")],
    "EMP-018": [(date(2026, 5, 21), "LEAVE", "Casual")],
    "EMP-020": [(date(2026, 5, 25), "LEAVE", "EL - Goa trip"),
                (date(2026, 5, 26), "LEAVE", "EL - Goa trip"),
                (date(2026, 5, 27), "LEAVE", "EL - Goa trip"),
                (date(2026, 5, 28), "LEAVE", "EL - Goa trip"),
                (date(2026, 5, 29), "LEAVE", "EL - Goa trip")],
}


def working_days(start: date, end: date):
    """Return all Mon-Sat dates in [start, end]. Indian 6-day work week assumption."""
    days = []
    d = start
    while d <= end:
        if d.weekday() < 6:  # 0=Mon ... 5=Sat
            days.append(d)
        d += timedelta(days=1)
    return days


def random_check_in(punctual: float) -> str:
    """Generate a check-in time. Punctual employees cluster around 9:15-9:30."""
    if random.random() < punctual:
        # punctual: between 9:00 and 9:35
        minute = random.randint(0, 35)
        hour = 9
    else:
        # late: between 9:35 and 10:30
        roll = random.random()
        if roll < 0.7:
            minute = random.randint(35, 59)
            hour = 9
        else:
            minute = random.randint(0, 30)
            hour = 10
    return f"{hour:02d}:{minute:02d}"


def random_check_out(check_in: str) -> str:
    """Generate a check-out time. Most people work 9-9.5 hours."""
    h, m = map(int, check_in.split(":"))
    total_minutes_in = h * 60 + m
    work_minutes = random.randint(540, 600)  # 9h to 10h
    total_minutes_out = total_minutes_in + work_minutes
    return f"{total_minutes_out // 60:02d}:{total_minutes_out % 60:02d}"


def generate_day(emp: dict, d: date) -> list:
    """Return one row (as a list) for this employee on this day."""
    date_str = d.isoformat()
    name = emp["name"]
    emp_id = emp["id"]
    notes = ""

    # 1. Public holiday — everyone gets HOLIDAY row
    if d in HOLIDAYS:
        return [date_str, emp_id, name, "HOLIDAY", "", "", "LEAVE", "Public holiday"]

    # 2. Sunday off — but we're using 6-day week, so no Sunday rows generated
    if d.weekday() == 6:
        return None

    # 3. Hand-crafted event for this employee on this day
    events = EMPLOYEE_EVENTS.get(emp_id, [])
    for event_date, status, event_notes in events:
        if event_date == d:
            if status in ("LEAVE", "ABSENT"):
                return [date_str, emp_id, name, status, "", "", "LEAVE" if status == "LEAVE" else "OFFICE", event_notes]
            if status == "HALF_DAY":
                check_in = random_check_in(emp["punctual"])
                # half day = leave by ~13:30
                h, m = map(int, check_in.split(":"))
                check_out = f"{13:02d}:{random.randint(20, 40):02d}"
                return [date_str, emp_id, name, "HALF_DAY", check_in, check_out, emp["loc"], event_notes]
            if status == "PRESENT":  # for FIELD visits
                check_in = random_check_in(emp["punctual"])
                check_out = random_check_out(check_in)
                return [date_str, emp_id, name, "PRESENT", check_in, check_out, "FIELD", event_notes]

    # 4. Normal day — generate based on patterns
    # WFH probability
    is_wfh = random.random() < emp["wfh_pct"]
    location = "WFH" if is_wfh else emp["loc"]

    check_in = random_check_in(emp["punctual"])
    check_out = random_check_out(check_in)
    status = "WFH" if is_wfh else "PRESENT"

    # Late note for very late check-ins
    h, m = map(int, check_in.split(":"))
    late_minutes = max(0, (h * 60 + m) - (9 * 60 + 30))
    if late_minutes > 20 and random.random() < 0.5:
        notes = random.choice([
            "Traffic on Outer Ring Road", "Auto delay", "Doctor appointment",
            "Bank work", "Apartment maintenance issue", "",
        ])

    return [date_str, emp_id, name, status, check_in, check_out, location, notes]


def main():
    start = date(2026, 5, 1)
    end = date(2026, 5, 30)  # last working day before today (June 1, Mon)
    days = working_days(start, end)

    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(["date", "employee_id", "employee_name", "status",
                     "check_in", "check_out", "location", "notes"])

    # May data
    for d in days:
        for emp in EMPLOYEES:
            row = generate_day(emp, d)
            if row:
                writer.writerow(row)

    # June 1 — today snapshot (kept identical to original sample-data.csv for continuity)
    today_rows = [
        ["2026-06-01", "EMP-001", "Arjun Mehta",     "PRESENT",  "09:25", "18:40", "OFFICE",  ""],
        ["2026-06-01", "EMP-002", "Priya Sharma",    "PRESENT",  "09:32", "18:30", "OFFICE",  ""],
        ["2026-06-01", "EMP-003", "Rohan Iyer",      "WFH",      "09:45", "19:10", "WFH",     "Firmware v2.3 release"],
        ["2026-06-01", "EMP-004", "Neha Reddy",      "LEAVE",    "",      "",      "LEAVE",   "Casual leave - family function"],
        ["2026-06-01", "EMP-005", "Vikram Singh",    "PRESENT",  "09:15", "18:50", "FACTORY", ""],
        ["2026-06-01", "EMP-006", "Kavya Nair",      "PRESENT",  "09:28", "18:35", "FACTORY", ""],
        ["2026-06-01", "EMP-007", "Aditya Krishnan", "PRESENT",  "09:20", "19:00", "FACTORY", ""],
        ["2026-06-01", "EMP-008", "Sneha Patil",     "PRESENT",  "09:30", "18:45", "FACTORY", ""],
        ["2026-06-01", "EMP-009", "Karthik Rao",     "PRESENT",  "09:18", "18:30", "FACTORY", ""],
        ["2026-06-01", "EMP-010", "Meera Joshi",     "HALF_DAY", "09:25", "13:30", "FACTORY", "Personal work in afternoon"],
        ["2026-06-01", "EMP-011", "Suresh Babu",     "PRESENT",  "09:35", "18:40", "OFFICE",  ""],
        ["2026-06-01", "EMP-012", "Ananya Gupta",    "ABSENT",   "",      "",      "OFFICE",  "No call no show"],
        ["2026-06-01", "EMP-013", "Rahul Verma",     "PRESENT",  "09:00", "19:30", "FIELD",   "Site visit - Infosys campus AQI install"],
        ["2026-06-01", "EMP-014", "Divya Menon",     "PRESENT",  "09:22", "18:35", "OFFICE",  ""],
        ["2026-06-01", "EMP-015", "Manish Kumar",    "PRESENT",  "09:40", "18:55", "OFFICE",  "Traffic on Outer Ring Road"],
        ["2026-06-01", "EMP-016", "Pooja Desai",     "WFH",      "10:00", "19:00", "WFH",     "Doctor appointment in morning"],
        ["2026-06-01", "EMP-017", "Sandeep Bhat",    "PRESENT",  "09:27", "18:40", "OFFICE",  ""],
        ["2026-06-01", "EMP-018", "Lakshmi Pillai",  "PRESENT",  "09:30", "18:30", "OFFICE",  ""],
        ["2026-06-01", "EMP-019", "Harish Naidu",    "PRESENT",  "09:15", "19:15", "OFFICE",  "Weekly all-hands prep"],
        ["2026-06-01", "EMP-020", "Ritu Aggarwal",   "LEAVE",    "",      "",      "LEAVE",   "EL - Goa trip till Wed"],
    ]
    for row in today_rows:
        writer.writerow(row)


if __name__ == "__main__":
    main()
