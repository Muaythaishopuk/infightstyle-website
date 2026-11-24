# INFIGHTSTYLE Fight League website: notes for Claude

Claude reads this file at the start of every session in this repository.
Keep it short. Detail belongs in `.claude/memory/`.

## This repository is public

The repository is public on GitHub and is the live website
(GitHub Pages, `main` branch, root folder, domain set in `CNAME`).

- Never write anything private here: prices, supplier details, customer
  names, fighter contact details, passwords, unannounced events.
- Anything pushed to `main` goes live within a minute or two.
- Files and folders starting with `.` (like this one) are not served on the
  website, but anyone can still read them on GitHub.

## How the site works

- Plain static site. No build step, no framework.
- Events live in `events.js`. The site sorts them into next and past by date.
- News posts live in `posts.js`. Newest first on `/news/`.
- Shared links (shop, Facebook, Instagram, emails) are at the top of
  `assets/site.js`. Styles are in `assets/style.css`.
- Poster and gallery images go in `images/`.
- Preview locally: `python3 -m http.server 8742 --directory .`
- Preview another date: add `?today=2026-10-01` to the address.
- `README.md` has the owner-facing instructions. Keep it in step with changes.

## Rules

- Do not change the `MX` DNS record or advise changing it. Email is hosted
  elsewhere.
- Do not delete or rename `CNAME`.
- Keep page addresses the same as the old site (table in `README.md`).
- The owner is not a developer. Explain changes in plain English.

## Memory

Notes that should survive between sessions live in `.claude/memory/`.

- At the start of a task, read `.claude/memory/plans.md`.
- When the owner decides something or asks for something that will not be
  finished this session, add it to `plans.md` in the same commit as the work.
- When something is finished, move it to "Done" with the date.
- When asked to "tidy memory": remove "Done" items older than a month,
  merge duplicates, fix anything the code now contradicts, then list every
  item still open and ask the owner about each one.
- One topic per file if `plans.md` grows past a screen or two. List new
  files in `.claude/memory/README.md`.
