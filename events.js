/*
 * ============================================================
 *  EVENTS — the only file you need to edit to update the site
 * ============================================================
 *
 *  Add a new event by copying one block below and changing it.
 *  The site works out by itself whether an event is "next" or "past"
 *  from its date, so you never need to move anything around.
 *
 *  date      "YYYY-MM-DD"  (e.g. "2027-02-14")
 *  poster    image file in the images folder, or "" for none
 *  entryUrl  Kihapp (or other) sign-up link, or "" for none
 *  prices    list of lines, e.g. ["Entry: £45", "Spectators: £20"]
 *  preview   paragraphs shown BEFORE the event (sell it, how to enter)
 *  writeUp   paragraphs shown AFTER the event (how it went); if left
 *            empty, the preview text is shown instead
 */
window.IFS_EVENTS = [
  {
    title: "The Big One — Infightstyle Open",
    tag: "Open tournament",
    date: "2026-11-01",
    venue: "The Hideout Sports Arena, Farnworth",
    poster: "poster-big-one-2026-11-01.jpg",
    entryUrl: "https://www.kihapp.com/tournaments/27551-ifs-big-open",
    prices: ["Entry: £45", "Spectator tickets: £20"],
    preview: [
      "Our biggest event of the year. The Big One Open Tournament is open to all fighters, giving competitors of every level the chance to test themselves in a high-quality, competitive event.",
      "Fighters and ticket holders can register now through Kihapp. Don't miss it!",
    ],
    writeUp: [
      "Our biggest event of the year: the Big One Open Tournament at The Hideout Sports Arena, open to fighters of every level for a high-quality, competitive day of junior Muay Thai.",
    ],
  },
  {
    title: "IFS Junior Novice Open",
    tag: "Novice tournament",
    date: "2026-09-20",
    venue: "Kearsley Muay Thai",
    poster: "poster-novice-open-2026-09-20.jpg",
    entryUrl: "https://www.kihapp.com/tournaments/27091-ifs-jnr-novice-open",
    prices: [],
    preview: [
      "A tournament just for novice junior athletes with 0–4 fights, giving developing fighters valuable competitive experience in a well-matched tournament.",
      "Athletes can register now through Kihapp.",
    ],
    writeUp: [
      "A tournament just for novice junior athletes with 0–4 fights, giving developing fighters valuable competitive experience in well-matched bouts.",
    ],
  },
  {
    title: "Ultimate Fight Night",
    tag: "Sister promotion",
    date: "2026-07-26",
    venue: "",
    poster: "",
    entryUrl: "",
    prices: [],
    preview: [
      "Ultimate Fight Night, our sister promotion, has been recognised as one of the UK's top Muay Thai shows for years. A stacked card of around 4–5 A-Class bouts, including a world title fight.",
      "Featuring Lewis George, back after a six-month training camp in Thailand; Louis Fairhurst, fresh off a huge win on Hitman Fight League and now stepping up for a world title; and Kieran Lee, returning against the experienced Connor Bourne.",
    ],
    writeUp: [
      "Ultimate Fight Night, our sister promotion and one of the UK's top Muay Thai shows for years, returned with a stacked card of A-Class bouts including a world title fight, featuring Lewis George, Louis Fairhurst and Kieran Lee vs Connor Bourne.",
    ],
  },
  {
    title: "IFS Junior Open Tournament",
    tag: "Novice & experienced",
    date: "2026-06-28",
    venue: "The Hideout Sports Arena, Farnworth",
    poster: "poster-junior-open-2026-06-28.jpg",
    entryUrl: "",
    prices: [],
    preview: [
      "An open tournament with two categories: 0–4 fights (novice) and 5+ fights (experienced). Athletes register through Kihapp.",
    ],
    writeUp: [
      "An open tournament at The Hideout Sports Arena with two categories: 0–4 fights (novice) and 5+ fights (experienced).",
    ],
  },
  {
    title: "IFS Junior League 3 — England vs Norway",
    tag: "Fight card",
    date: "2026-02-01",
    venue: "The Hideout Sports Arena, Farnworth",
    poster: "poster-league-3-2026-02-01.jpg",
    entryUrl: "",
    prices: [],
    preview: [],
    writeUp: [
      "Infightstyle Junior League 3 marked another major step forward in the rapid rise of the promotion. The traction from our first two events had spread beyond the UK, with international gyms reaching out to bring their fighters over to compete.",
      "Headlining the show was a standout England vs Norway C-Class bout, adding an international edge to the card. A clip from the fight went viral, hitting over 10 million views on Instagram, showing the exposure and platform the league can now offer.",
      "Once again the event delivered high-standard matchmaking, organisation and atmosphere. League 3 confirmed it: this is evolving into an international platform for junior Muay Thai.",
    ],
  },
  {
    title: "IFS Junior League 2",
    tag: "Fight card",
    date: "2025-10-19",
    venue: "",
    poster: "poster-league-2-2025-10-19.jpg",
    entryUrl: "",
    prices: [],
    preview: [],
    writeUp: [
      "Following the huge success of our debut, Infightstyle Junior League 2 delivered another statement performance on the UK junior Muay Thai scene.",
      "Designed as a smooth, efficient Sunday show, the whole event was finished by 5PM, ideal for juniors, coaches and families travelling from across the country.",
      "One of the standout fights saw Tommy Gunn (Thai Fist) take on Zander (Majestic Gym) in a high-level contest that showcased the technical ability and heart of the UK's next generation.",
    ],
  },
  {
    title: "IFS Junior League 1",
    tag: "Our first event",
    date: "2025-06-21",
    venue: "",
    poster: "poster-league-1-2025-06-21.jpg",
    entryUrl: "",
    prices: [],
    preview: [],
    writeUp: [
      "The first Infightstyle Junior League made a huge statement in the UK Muay Thai scene and instantly positioned us as a serious new force in junior show promotion.",
      "We delivered a stacked card featuring some of the best junior talent in the UK in competitive, well-matched bouts, and gave a platform to experienced juniors making their N and C-Class debuts.",
      "Topping the card was a standout European matchup between Stan Venables and Omar Qari, a fitting headline for a show that set the tone for everything Infightstyle Junior League represents.",
    ],
  },
];
