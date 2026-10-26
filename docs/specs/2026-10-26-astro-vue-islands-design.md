# Photo Kruzhok Astro and Vue islands

Date: 2026-10-26

This document replaces the frontend architecture of `docs/specs/2026-10-23-photo-kruzhok-design.md`. The API, roles, domain rules, error envelope, and image pipeline in that document stay in force. Where the two documents disagree about apps, routing, React, a separate landing page, or a dark theme, this document wins.

## Goal

One website a reviewer can open. Astro renders the public pages. Vue hydrates only the controls that need a session. SCSS is the only style source. The audience is a local photography group. There is no marketing landing page and no goal of acquiring strangers.

## Non-goals

A separate React application. A separate Vue application. A separate landing application. A second Vue or React router. A hand-written masonry layout in JavaScript. Loading Fancybox on the first paint of the gallery. Downloading channel photos on every seed run.

## Applications

The only frontend package is `apps/web`. It is an Astro application. `apps/landing` and `apps/admin` are removed. `packages/ui` keeps the SCSS kit and the Vue components. React wrappers in `packages/ui` are removed. `packages/sdk` stays the API client. `apps/api` stays Django.

Astro owns every route. A Vue file is an island on an Astro page. It does not choose the URL.

| Route | Renderer | Vue island |
| --- | --- | --- |
| `/` | Astro photo grid | none |
| `/posts/[id]` | Astro photo, caption, EXIF, visible comments | like and comment form |
| `/profiles/[username]` | Astro profile and visible posts | none |
| `/login` | Astro page | sign-in form |
| `/register` | Astro page | registration form |
| `/posts/new` | Astro page | upload form |
| `/challenges/current` | Astro page | submission and vote |
| `/panel/challenge` | Astro page | theme editor and vote |
| `/panel/moderation` | Astro page | hide and restore |
| `/panel/stats` | Astro page | counts |

There is one sign-in for the whole origin. The refresh cookie remains `pk_refresh`. The access token stays in memory inside the Vue island that needs it. On a full page load, that island calls refresh once and then uses the new access token. A guest who hits like, comment, upload, or vote is sent to `/login`.

A leader uses the same sign-in and then opens `/panel/challenge`, `/panel/moderation`, or `/panel/stats`. A non-leader response of `403` with code `permission_denied` renders the Russian sentence `Недостаточно прав`.

## Data

Public Astro pages call the existing API without a token: `GET /api/posts`, `GET /api/posts/{id}`, `GET /api/posts/{id}/comments`, and `GET /api/profiles/{username}`. Vue islands call the same API through `packages/sdk`. Errors stay `{ code, message, fields }`. A field error is tied to that field. A hidden post is absent from the grid and from the public profile. A direct request for it by a guest renders the not-found page.

The first 24 photographs come from the public Telegram channel `https://t.me/PostSovietPhotography`. `scripts/fetch_channel_photos.py` downloads exactly 24 images once, writes them under `apps/api/fixtures/photos/`, and records each file in `CREDITS.md` with the channel name and the author named on that post. When the post names no author, the credit is the channel. The channel owner permits these files in this demo, including resized WebP and AVIF derivatives. `seed_demo` only reads that folder and sends each file through the existing upload pipeline. Running the command twice still leaves 24 posts. The command does not open a network connection. Later photographs come only from a member upload.

## Appearance

SCSS is the only authoring language for styles. The browser receives compiled CSS. Hand-written `.css` sources are not added.

Color tokens stay CSS custom properties in `oklch`. Light values stay the current set: `--pk-color-bg` is `oklch(0.9679 0.005 78.3)`, `--pk-color-surface` is `oklch(1 0 0)`, `--pk-color-text` is `oklch(0.2178 0 0)`, and `--pk-color-accent` is `oklch(0.4698 0.143 37.3)`. Derived hover, muted text, and border keep the existing `oklch(from …)` declarations.

Dark theme overrides those same names inside `@media (prefers-color-scheme: dark)`. Dark values are `--pk-color-bg: oklch(0.18 0.005 78.3)`, `--pk-color-surface: oklch(0.23 0.005 78.3)`, `--pk-color-text: oklch(0.93 0 0)`, and `--pk-color-accent: oklch(0.72 0.12 37.3)`. Hover, muted text, and border are derived from these with the same relative-color expressions. There is no second set of token names.

The home gallery is full width. It is a CSS grid in the manner of a justified photo grid. A masonry library is added only after a test shows that the CSS rows overlap or leave a broken gap. That library is pinned to an exact version at the moment it is added. No masonry JavaScript is written by hand.

Opening a gallery image uses Fancybox. The implementation plan pins the exact Fancybox version on the day it is added. The script loads on the first open, not in the initial gallery response. Its colors come from the tokens.

The post page, profile, forms, and panel are a column of at most `72ch`. Gallery and column share the same type, link color, and background.

Interface copy is Russian. `lang="ru"`.

## Tests

An Astro build test asserts that the home HTML contains the grid and does not contain an `astro-island` element. It also asserts a post page and a profile page. Vitest covers the Vue islands: sign-in, registration, upload, like, comment, vote, the three panel screens, and the forbidden sentence `Недостаточно прав`. Existing Django API tests stay. The seed test still expects 24 posts after two runs, and it expects the command not to download anything. Playwright covers the grid, one post, sign-in, and one panel page. There is no React test suite.

## Superseded statements

These sentences in the 2026-10-23 spec no longer apply:

- A React application is a separate product surface.
- An Astro landing page is separate from the application.
- A Vue panel is a separate Vite application.
- A dark theme is a non-goal.
- The home page JavaScript budget assumes no lightbox. Fancybox is allowed, and only after the first open.
