---
name: roblox-game-builder
description: Use when a game is planned, built, launched or run on Roblox, or a web game is ported there — "игра для Roblox", "делаем в Roblox", "перенеси на Roblox", "сверь идею/план с Roblox-правилами", "как продвигать в Roblox", "реклама Roblox", "тамбнейл", "почему мало игроков / упал CCU", "Home Recs, D1/D7, bounce", "монетизация Robux", "live ops / апдейты", "как должна выглядеть Roblox-игра / UI / VFX / экономика", "веб-игра по Roblox-референсу". Practitioner playbook distilled from Roblox devs with $25–131K/mo games (channel Tap + similar channels): idea and market gates, the 8 design blocks, 5 virality factors, first 90 s, production with AI, test place and timed alt-account tests, launch with Sponsored Ads, the funnel PTR → bounce → D1/D7/D28, consumable monetisation, weekly live-ops cycle, diagnosis table, mistakes; plus the look, UI, VFX, economy and F2P pacing of 45 top Roblox games with key frames (RobloxLibrary). Also audits Alex's current idea/plan/references against these rules.
---

# Roblox game builder

Roblox is a **winner-takes-all recommendation market**: the algorithm compares your stats with **experiences with similar players** and gives Home Recs to the better one. Every step below serves that comparison: a clickable fantasy (PTR), a first minute that keeps the promise (bounce), a loop with depth (D1/D7/D28, playtime), spend days (monetisation), and weekly updates that each lift one stat.

This skill is the Roblox layer over the factory pipeline, not a replacement: `game-project-workflow` stays the lead (`<GameFactory>/WORKFLOW.md`), `DESIGN/CONSTITUTION.md` and `IDEA_FILTER.md` stay the filter, `game-idea-scout` finds and checks ideas, `DESIGN/ROBLOX.md` holds the tech (Luau server/client, Rojo, DataStore, Studio MCP). Where the sources and the constitution disagree, the constitution and Alex's ТЗ win; note the conflict.

**References** (`references/`, notes with `[videoId MM:00]` timecodes; transcripts in `<GameFactory>/RobloxLibrary/transcripts/`, local only):
- `design.md`: 8 design blocks, virality, first session, production speed, AI-made games.
- `algorithm-ads.md`: algorithm signals, Sponsored Ads, 500 highly engaged, funnel, diagnosis, title/thumbnail packaging.
- `liveops-money-thumbs.md`: live-ops cycle, monetisation, AI thumbnails, idea hunting outside Roblox.
- `cases.md`: the author's own games with real numbers, team and hiring, AI workflow.
- `similar-channels.md`: rasdev, MoseyTube77, Zyonic, waveshine, DitchyDevelopments: where they agree with Tap, what they add, where they disagree (⚠).
- `sources.md`: video list with links.

**Look and feel library** (`<GameFactory>/RobloxLibrary/`): `STYLE.md` (two game forms, F2P first-session pacing, what hooks, visual poles, HUD, VFX minimum, economy, offer moments Roblox → rewarded web, anti-examples), `REFS.md` (which key frames to open for a task + palettes of 41 games), `notes/<channel>.md` (per-game breakdowns). Open `STYLE.md` at stages 2–3 and 8, and `REFS.md` frames before designing HUD, shop, rebirth, index or VFX.

**Web games from a Roblox reference** use this library for mechanics, pacing, economy, VFX and the fantasy format only: characters, avatars and UI are our own, with no Roblox/Minecraft look (Google bans the game and the publisher account: `LESSONS/platforms.md`); the style comes from `StyleLibrary`.

Open the reference of the stage you are in; quote the rule with its timecode when you rely on it.

## Mode «сверка» (audit Alex's idea, plan, project or references)
Triggered by «сверь», «проверь по Roblox-правилам», or at the end of each workflow stage of a Roblox game. Read the project's `docs/IDEA.md`, `GAME_SKELETON.md`, plan and refs, then go through the gates of every stage reached so far and write `docs/ROBLOX_CHECK.md`:
- per gate: ✅ / ⚠️ / ❌ + one line of evidence from the project files + the rule's source;
- top 3 fixes, each tied to the stat it moves;
- conflicts with the constitution or ТЗ, listed apart.

Done when every gate of the reached stages has a mark with evidence. In chat: ≤ 10 lines, the ❌ first.

## Stages and gates

### 1. Idea and market
- **Fantasy as a verb:** role + action + feeling, readable from the title and one picture. Test: a 9-year-old explains it to a friend at lunch in one sentence.
- **Proven demand with a number**, ideally outside Roblox (Steam wishlists/reviews, CrazyGames/Coolmath votes, mobile downloads, YouTube views, «where can I play» comments) → run `game-idea-scout` mode «одна идея» (`scout_compete.py`).
- **Market phase:** first to market → fine; red ocean (≥ 3 strong games, same titles and thumbnails) → only with a mutation; **purple ocean** = high demand in Creator Exchange + weak execution → play the leaders and make it 10× better.
- **Change the reference meaningfully:** ≥ 20 % new for a 1–10K CCU target, ~40 % stacked changes for 100K; one unique system the genre lacks. Every system you take must already be proven in a top game. Templates, reskins and copied titles/thumbnails are deprioritised by Roblox.
- **Fit:** simple to consume, deep, replayable, works on mobile (≈ 80 %) and console, mass appeal; enter a rising trend before its peak (90-day CCU curve), not a front-page hit at its peak.
- **Audience and money:** profit over CCU (≈ $5–7 per average CCU per month); with no ad budget, a 16+ game is the realistic start (new games are shown 16+ until 500 highly engaged players; one source reports 100 for under-16 games: verify in the Creator Dashboard).
Gate: fantasy sentence + demand number with source + phase + our 20 % change written in `docs/IDEA.md`.

### 2. Design (before any code)
- **8 blocks:** fantasy · unique mechanic · core loop «leave the base → get the thing → bring it back» · RNG (before and after the action) · level design that serves play (central hub, short paths, biome change) · tension (threat, PvP, timer) · progression · collection/index.
- **5 virality factors:** clickable fantasy; onboarding ≤ 90 s with a short cutscene and one mechanic at a time; 10× more fun with friends + **social flex visible at spawn** (rare pets/blocks, base); simple mechanic with depth and mobile UX (big buttons, buy 1/N/max); **clipable moments** (ragdoll into the void, big reveals).
- **Cause and effect** on every action: press → sound + VFX + camera shake → visible result.
- **Depth over complexity:** PvP or social systems keep strategy unsolved; cut accelerators that reach the endgame in hours.
- **Return hooks:** something new tomorrow (ingredient, pet, base tier), weekly event, sunk cost (base, collection); free retention set: offline income with a popup on join, free chest for like + group, codes, daily wheel, friend boost.
- **Pick the form:** endless «+1» simulator (index, rebirths, D7/D28) or a 20–60 min game with an end (one global meter, joke finale, replay modes); the title as «verb + absurd object (+ silly tool)»; social chaos (deceive, push, write threats for others) beats plain competition. Odds shown before each try, progress visible on the body or the world, a tool ladder from pathetic to insane (`STYLE.md` §1, §3).
- **Look:** HUD layout, window style, outlined fonts, event words, VFX minimum: `STYLE.md` §4–6, frames in `REFS.md`.
Gate: the 17-column skeleton has every block filled, columns 14 «Люди» and 16 «Монетизация» written for Roblox, first minute laid out by seconds.

### 3. First session (the stat Roblox reads first)
- Keep the title's promise within 10–30 s (first play bounce counts the first 60 s; ~20 % is too high).
- First action = the most engaging mechanic and a **wow moment**; items auto-equipped, nothing to buy or read first; genre signalled by action, not text.
- Teach the loop «get the thing → get money from it → progress», then let go; later mechanics by contextual triggers (1K cash → trails).
- Tease progression in the first roll (silhouettes of rare items).
- Targets: 95 % still playing at 30 s, 87 % at 1 min, 65 % at 5 min; tutorial completion ≈ 77 % is good.
- Genre pacing on a fresh account (median of 15 simulators, `STYLE.md` §2): first action ≤ 6 s, first purchase ~24 s, first upgrade and tutorial done ~1 min, first rarity ~1 min (rig the first drop), rebirth or world 2 ~2 min, first wall at 2–2.5 min and cleared by 1–3 min of grind; hard walls only after minute 5. One quest line at top centre + chevrons on the ground; HUD buttons appear one at a time.
Gate: every onboarding step is a custom funnel event; timed run on a fresh alt account meets the targets.

### 4. Build
- Tech, project layout and tools: `DESIGN/ROBLOX.md` (Rojo + Luau, server-authoritative economy, ProfileStore-level saves, Studio MCP only when needed).
- MVP = the core loop only; prototype it fast (AI-assisted, hours, not weeks), then models and UI from an art style guide with AI refs (one style, set from day 1); `game-art-first` for the look, Steam style approved by Alex.
- Level small enough that the path to the action is short; mobile and console controls from the first build.
- Keep a separate **published test place**: live Roblox bugs do not show in Studio.
Gate: loop playable on PC, mobile and console in the test place; `game-autotest`-style smoke where it applies.

### 5. Test and balance before launch
- Play your own game a lot, as a newcomer, on mobile and console; fresh alt account with a timer for every milestone (min 1 — first upgrade…).
- 2–3 paid testers (~1–2K Robux for ~3 h of grind) with a template: price, time, where stuck; balance from their data before launch, not on the live algorithm.
- 8–10 core playtesters for later updates (Discord).
Gate: no progression wall in the first 10 min; milestone times written in `docs/ROBLOX_BALANCE.md`.

### 6. Packaging and launch
- **Title:** keyword research in Creator Exchange (several games with millions of visits on the word), 3rd-grade reading level, templates «Verb a Noun / Be a Noun / Escape the Noun» + a built-in challenge; it must not mislead about the loop.
- **Thumbnails:** feeling and fantasy in one frame, 1–2 characters, big emotions, simple background, high contrast, text on clean sky, core loop shown; check every variant in qptr.io on mobile/desktop/console. Make many (AI, 100+), keep 10–20 very different for ads; 2–3 new concepts a week; a **gameplay video** on the page (without it ~2.5 % of clickers play) and the free gameplay video on the tile (+31–39 % playtime reported). Promo assets via `game-promo-kit`.
- **Ads:** Sponsored Ads, daily budget ≥ $16 (pay in Robux → ad credits), ≥ 3 days, ideally a week; recommended targeting, nothing advanced. Cold ad traffic looks bad: wait ~3 days for stats, judge by the benchmark. Optional beta mode: optimise on ad traffic while hidden from Home Recs. No money → short-form video (TikTok/Shorts).
- **Stop ads** when 7-day Home Rec impressions exceed sponsored ad impressions; restart briefly after a big update.
- Ads buy data, not rank. Alternative recipe (MoseyTube77): $10/day × 10 days, keep going at CTR ≥ 2.5 % and cost per play ≤ $0.008. Sources disagree on ads from day 1 vs only after retention is proven, and daily vs lifetime budget: `similar-channels.md` «Запуск и реклама».
Gate: title + ≥ 10 thumbnails + video + ad plan with budget; Alex approves the spend (money is his decision).

### 7. Funnel and updates
Funnel: impression → PTR (play-through rate) → first play bounce → return windows D1, D2–7, D8–28 (ranking counts players who came from Recommended), plus playtime, payer conversion, ARPPU. Look at Analytics → Acquisition → Home Recommendations against **Benchmark: experiences with similar players**, never «vs genre». Rolling 7-day window: judge an update after a week.
- Each update is a **hypothesis for one stat**, the worst one first: «if I add/remove/improve Y, X grows», backed by three sources: player feedback (AI summary in Creator Dashboard, Discord), competitors you are compared with, your numbers (funnels by device and traffic source, first-session retention drops).
- Ship, check, keep or revert; use Experiments (A/B) for updates and thumbnails.
- What moves which stat: diagnosis table in `algorithm-ads.md` §3.
Gate: every update in `docs/ROBLOX_UPDATES.md` has target stat, hypothesis, sources, result.

### 8. Monetisation
- Gameplay before monetisation; nothing pay-to-win or economy-breaking (no cheap cash packs, no raw auto-collect).
- **Consumable dev products** for repeatable benefits (2x, lock, boost, instant hatch) → 7-day spend days; game passes for permanent upgrades and whales, three price tiers.
- Free version of the relief first (base lock 60 s), paid stronger one after (24 h). Offer at the moment of benefit (collect offline cash → «2x for 19 R$»).
- 3 purchase paths per product (HUD button, «+» by the currency, context); auto-open the shop only from the 3rd shortage, ≤ 3–5 times a session; paid items at the busiest POIs.
- Streak restore and other «pain → consumable» offers; currency «+» and in-world NPC sellers.
- Cheap stackable entry products (5–9 R$); limited cosmetics with real scarcity (100–1000 units) from day 1.
- Judge a product by D1/D7/playtime as well as Robux.
Gate: column 16 lists each product with the pain it removes, its moment and place.

### 9. Live ops (weekly)
Sat plan → Sun tasks → Mon–Wed build → Thu ready → Fri playtest (internal + core) → Sat release. Patches (bugs, exploits, balance) any day; a critical exploit the same day. Each update targets a Home Recs metric; D28 needs deep progression (index, new ways to interact), not +1 skin. Stay in the community; do not hand out rare items under pressure.

## Mistakes the sources paid for
Reskin of a front-page hit; misleading title; two mechanics taught at once; manual equip or shop trip in onboarding; testing only on a levelled account; balancing on the live algorithm; whale products added weeks late; thumbnail unreadable on mobile; no page video; too big a map; copying a mechanic across genres (auto roll broke a PvP economy); «more ads» for a dying game instead of an update; dropping a game after the first flop; months of building before any data.

## Rules
- Inspiration, not cloning: take the fantasy type, loop structure and metrics practice; names, characters, art, maps and thumbnails are ours (see «копирование: не берём» in the references).
- Numbers are the authors' as of 2025–2026 with their source; platform rules (16+ gate, metrics, ad minimums) change: verify on create.roblox.com/docs or the Creator Dashboard before relying on them.
- Spending money (ads, testers, publishing), publishing and posting happen only on Alex's explicit yes.
