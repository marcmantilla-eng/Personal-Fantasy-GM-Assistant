# Fantasy Football Assistant (Phase 3 — Read-Only Yahoo Connection)

This is a personal Fantasy Football assistant. Out of the box it runs on
**made-up, fake league data** — it is not connected to your real Yahoo
Fantasy account and cannot see or change anything about your real team
until you deliberately connect it (see "Connecting your real Yahoo
account" below).

Even once connected, this app is **read-only**: it can look at your real
league, roster, matchups, and free agents, but it will never change your
lineup, add or drop a player, submit a waiver claim, or make a draft pick
on your behalf. Every recommendation is something you'd have to go action
yourself on Yahoo.

## What this prototype does

- **Roster & Lineup** — Shows a fake team's roster, flags injuries/bye
  weeks/questionable players, and recommends the best legal starting
  lineup, with plain-language reasons for every suggested change.
- **Waiver Wire** — Suggests fake "free agent" pickups and which bench
  player you'd drop for them, with an explanation for each.
- **Matchup** — Compares your fake team's projected score against a fake
  opponent for the week.
- **Draft Assistant** — Shows a draft board with rankings adjusted for
  your team's positional needs. (Yahoo has no official way for an app to
  submit live draft picks, so this stays advisory-only either way.)
- **Setup** — Lets you connect your real Yahoo account and choose which
  league/team to use, or switch back to mock data at any time.

Every recommendation includes a plain-language explanation and, where
relevant, a confidence level. Nothing on any screen submits, saves, or
changes anything on Yahoo — it's all for you to read and decide on
yourself.

Some numbers Yahoo's API doesn't provide (like weekly point projections)
are estimated from recent scoring and are always marked with an
**Estimate** badge, so you always know what's a real Yahoo number and
what's a guess.

## What this app does NOT do

- It does **not** change your real Yahoo lineup, add/drop players, submit
  waiver claims, or make trades or draft picks — even once connected.
- It does **not** use any browser automation, scraping, or unofficial
  Yahoo endpoints — only Yahoo's official Fantasy Sports API.
- It does **not** ask you to type your Yahoo password anywhere in this
  app. Connecting uses Yahoo's own sign-in page in your browser.

## How to start it (Windows, step by step)

1. Open the `yahoo-fantasy-assistant` folder in File Explorer.
2. Double-click the file named **`Start Fantasy Assistant.bat`**.
3. A black window will pop up and do some one-time setup the very first
   time you run it (this can take a minute or two — you'll see some text
   scroll by, that's normal). On every run after that, this step is
   almost instant.
4. Your web browser will open automatically to the dashboard. If it
   doesn't open by itself, open any browser (Edge, Chrome, etc.) and go
   to this address:

   ```
   http://127.0.0.1:5055
   ```

   (This address only works on this computer — it is not a public
   website, and nobody else can visit it.)

5. Use the tabs at the top of the page to move between **Roster &
   Lineup**, **Waiver Wire**, **Matchup**, **Draft Assistant**, and
   **Setup**.

## Connecting your real Yahoo account (optional)

By default the app runs entirely on fake mock data — nothing is sent to
Yahoo or the internet. If you'd like it to show your *real* league
instead:

1. Register a free app at Yahoo's developer site to get a **Client ID**
   and **Client Secret**. When asked for API permissions, choose
   **Fantasy Sports — Read** only. For the redirect/callback, use `oob`
   (this app has no public website, so Yahoo shows you a code to paste
   in instead).
2. Copy `.env.example` to a new file named `.env` in this folder, and
   fill in your Client ID and Secret. This file is never uploaded to
   GitHub (it's listed in `.gitignore`) and the app never displays or
   logs its contents.
3. Start the app and open the **Setup** tab.
4. Click **Connect to Yahoo**. Your browser will open to Yahoo's sign-in
   and permission page. Yahoo will show you a short code — copy it and
   paste it into the black console window this app is running in (not
   into the web page), then press Enter there.
5. Back on the Setup tab, choose your league and team from the
   dropdowns, check the box to use live data, and click **Save**.

You can switch back to mock data at any time from the Setup tab by
unchecking that box.

## How to stop it

Close the black window that popped up when you started the app (or press
`Ctrl+C` inside it, then press any key when prompted). Closing your
browser tab does **not** stop the app — the black window is what's
actually running it.

## If something goes wrong

- **"Python was not found" or setup fails**: Python needs to be
  installed on this computer first. Let me know and I'll help you check.
- **The browser shows "can't connect" or "site can't be reached"**: The
  black window may have closed, or setup may still be running. Try
  double-clicking the launcher file again.
- **Anything else looks wrong**: Just describe what you see — a
  screenshot helps a lot — and we'll fix it together.

## What's inside this folder (for reference — you don't need to touch these)

```
yahoo-fantasy-assistant/
├── Start Fantasy Assistant.bat   <- Double-click this to launch the app
├── run.py                        <- Tells the app how to start
├── requirements.txt              <- List of small components the app needs
├── .env.example                  <- Template for your Yahoo credentials (copy to .env, fill in)
├── README.md                     <- This file
├── app/
│   ├── models.py                 <- Definitions of what a "player", "team", etc. look like
│   ├── mock_data/                <- The fake league data used when not connected to Yahoo
│   ├── yahoo_integration/        <- Talks to your real Yahoo account (read-only)
│   ├── recommendations/          <- The logic that generates suggestions
│   ├── data_source.py            <- Decides whether to use mock or real Yahoo data
│   ├── user_settings.py          <- Remembers your chosen league/team (not a secret)
│   └── dashboard/                <- The web dashboard (pages, styling)
├── tests/                        <- Automated checks that the suggestion logic works correctly
├── logs/
│   └── audit_log.csv             <- A running record of what the app looked at and suggested
└── venv/                         <- A private, isolated copy of the components this app needs
                                       used only by this app — doesn't affect the rest of your computer
```

Two files the app creates for you are never uploaded to GitHub: `.env`
(your Yahoo credentials) and `oauth2.json` (your saved login session).

## About the audit log

Every time you view a screen, the app writes a line to
`logs/audit_log.csv` recording what it checked and what it suggested.
You can open this file directly in Excel. This is here so there's always
a plain record of what the assistant has looked at and recommended —
this will become more important in later phases once real actions are
involved.

## Running the automated tests (optional, only if you're curious)

The recommendation logic (deciding lineups, alerts, waiver suggestions,
and draft rankings) has automated tests that check it behaves correctly.
You don't need to run these yourself, but if you want to:

1. Double-click **`Run Tests.bat`** in this folder.
2. You should see a line at the end saying something like
   `29 passed` — that means all checks succeeded. These tests run
   entirely offline against sample data, never against your real Yahoo
   account.

## What's next

Future phases may add draft-day and weekly lineup *recommendations* that
go further (Phase 4), optional notifications (Phase 5), and — only if
Yahoo's rules permit it for this kind of app, and only with your
explicit approval each time — the ability to actually submit a lineup
change or waiver claim rather than just suggesting one (Phase 6).
