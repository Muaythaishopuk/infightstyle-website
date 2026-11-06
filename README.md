# Infightstyle Fight League website

A rebuild of www.infightstylefightleague.co.uk (was GoDaddy Website Builder), as a plain
static site that can be hosted for free.

## Updating the site

**Almost everything you'll change is in `events.js`.**

- **New event:** copy one `{ ... }` block in `events.js`, then change the title, date,
  venue, poster and Kihapp link. Put the poster image in `images/`.
- **After an event:** fill in its `writeUp` with how it went.
- You don't need to move events between "Next" and "Past". The site does that by date.
  If no event is coming up, the home page and Next Events page say "Next event announced soon".
- **Preview another day:** add `?today=2026-10-01` to the address to see the site as it
  would look on that date.
- **News / blog post:** copy one `{ ... }` block in `posts.js`. Newest dates show first on `/news/`.
- **Gallery photos:** add the file to `images/` and copy one `<a>…</a>` line in
  `gallery/index.html`.
- Links (shop, Facebook, Instagram, emails) are at the top of `assets/site.js`.

Or just ask Claude: "add the IFS Junior League 4 event on 14th Feb, here's the poster".

## Pages (same addresses as the old site)

| Address          | File                        |
|------------------|-----------------------------|
| `/`              | `index.html`           |
| `/gallery/`      | `gallery/index.html`   |
| `/next-events/`  | `next-events/index.html` |
| `/past-events/`  | `past-events/index.html` |
| `/sponsors/`     | `sponsors/index.html`  |
| `/contact-us/`   | `contact-us/index.html`|

## Viewing it on this computer

```bash
python3 -m http.server 8742 --directory .
```

Then open http://localhost:8742

## Going live (GitHub Pages, free)

1. Create a GitHub repository and upload the **contents** of `` (with `CNAME` at the top level).
2. In the repository: Settings → Pages → deploy from the `main` branch, root folder.
3. In GoDaddy → the domain → DNS, change only the website records:
   - `A` records for `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `CNAME` for `www` → `<your-github-username>.github.io`
4. **Do not touch the `MX` record** (`mailserver.livemail.co.uk`). That's your email, and it
   isn't hosted by GoDaddy.
5. When the new site shows up at the address, tick "Enforce HTTPS" in GitHub Pages and
   then cancel the GoDaddy **Website Builder** plan. Keep the **domain** registration.
