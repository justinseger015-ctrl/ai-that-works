# riverside

A browser automation module for creating recording sessions on Riverside.fm. Used to schedule "AI That Works" podcast episodes without manually filling out the Riverside UI.

## Usage

The module is invoked via its `cli` submodule:

```bash
python -m riverside.cli \
  --title "Building AI Agents" \
  --episode-number 42 \
  --description "We discuss how to build production AI agents." \
  --date 2026-02-17
```

### Required Arguments

| Argument | Short | Description |
|---|---|---|
| `--title` | `-t` | Episode title |
| `--episode-number` | `-n` | Episode number (integer) |
| `--description` | `-d` | Episode description |
| `--date` | | Recording date in `YYYY-MM-DD` format |

### Optional Arguments

| Argument | Short | Description |
|---|---|---|
| `--guests` | `-g` | Comma-separated guest emails |
| `--headless` | | Run browser in headless mode |

### Environment Variables

| Variable | Description |
|---|---|
| `RIVERSIDE_LOGIN` | Riverside.fm login email (required) |
| `RIVERSIDE_PASSWORD` | Riverside.fm password (required) |

## Flow

```
CLI (cli.py)
  └── parse & validate arguments
      ├── format title: "{title}: 🦄 AI That Works #{episode_number}"
      ├── ensure default guest (dexter@humanlayer.dev) is in guest list
      ├── build SessionDetails(name, description, date=10:00 AM, duration=60)
      └── with RiversideAgent() as agent:
              └── agent.run(session)
                    ├── login()
                    │     ├── navigate to riverside.fm
                    │     ├── fill email + password
                    │     ├── submit login form
                    │     └── verify redirect to dashboard
                    │
                    └── schedule_session(session)
                          ├── _open_new_session_form()
                          │     ├── click "Schedule" in sidebar
                          │     ├── click "+ New" → "Session"
                          │     └── wait for form
                          │
                          ├── _fill_session_name(name)
                          ├── _fill_description(description)
                          ├── _set_timezone_pst()
                          ├── _add_session_guests(guests)
                          ├── _set_session_date(date)
                          │     ├── open calendar picker
                          │     └── navigate months → click target day
                          │
                          ├── _set_session_time(date, duration_minutes)
                          │     ├── select start time from dropdown (10:00 AM)
                          │     └── select end time from dropdown (11:00 AM)
                          │
                          └── _submit_session()
                                ├── click "Create" button
                                └── return session URL
```

### Step-by-step

1. **CLI parses arguments** and formats the session title as `{title}: 🦄 AI That Works #{episode_number}`. The default guest `dexter@humanlayer.dev` is always included.

2. **`RiversideAgent`** is a context manager that launches a Playwright-controlled Chromium browser (visible or headless). On exit it closes the browser cleanly.

3. **`login()`** navigates to Riverside.fm, fills in credentials from environment variables, submits the form, and verifies the redirect to the dashboard.

4. **`schedule_session()`** drives the scheduling UI step by step:
   - Opens the new session form via the Schedule sidebar.
   - Fills in name, description, and timezone (always Pacific Time).
   - Invites each guest by typing their email and pressing Enter.
   - Uses the calendar picker to navigate to the correct month and click the target day.
   - Selects 10:00 AM start and 11:00 AM end from the time dropdowns.
   - Submits the form and captures the resulting session URL.

5. **Debugging**: if a `screenshot_dir` is provided, numbered screenshots are saved at each major step to help diagnose UI changes.

## Module Structure

```
src/riverside/
├── __init__.py           # Exports: RiversideAgent, SessionDetails, schedule_riverside_session
├── cli.py                # CLI entry point (argparse)
├── riverside_agent.py    # Browser automation (Playwright) + SessionDetails dataclass
└── schedule_session.py   # Standalone test/demo script
```

## Key Defaults

| Default | Value |
|---|---|
| Session start time | 10:00 AM PST |
| Session duration | 60 minutes |
| Default guest | `dexter@humanlayer.dev` |
| Title format | `{title}: 🦄 AI That Works #{episode_number}` |
| Timezone | Pacific Time |
