# Photo Kruzhok portfolio design

Date: 2026-10-23

This document is the product spec for photo-kruzhok.

## Goals and non-goals

### Goals

The project is a portfolio. The success criterion is a reviewer who can see the stack in one visit. The photo circle is a plausible domain and a live demo, not a community that must be operated.

The finished MVP includes:

- A React application: a masonry feed with infinite pagination, photo upload and EXIF, likes and comments with optimistic updates, and profiles.
- An Astro landing page: a showcase, announcements, and public profiles. Lighthouse 95 or higher on the home page and on the static demo profiles.
- A Vue panel: the weekly theme, voting, moderation, and statistics.
- A shared SCSS/BEM UI kit and a typed SDK generated from OpenAPI.
- A monorepo, Docker Compose, CI, frontend deploy on Vercel, and the API on Railway.

Specs, a failing test before the code, and an explicit API contract are part of the work. AI assistance does not skip those gates.

### Non-goals

Follows, direct messages, notifications, search, albums, social login, realtime updates, mobile apps, a language switch, payments, recommendations, a photo editor, and mailing lists.

A dark theme, Next.js, a Sentry browser SDK on the landing page, Prometheus, and screenshot baseline tests.

Demo passwords, and any instruction for how to obtain them, do not appear in the README or the interface. The Django admin is not a product screen.

### License

The repository license replaces the current MIT text with the official PolyForm Strict 1.0.0 text. Copyright line: Aleksey Kerkin, 2024–2026. Non-commercial running is allowed. Redistribution, modified versions, and commercial use are not granted. Commercial use requires a separate written agreement with Aleksey Kerkin. The license file contains the official text, not a paraphrase.

Demo JPEGs keep their own license. That license must allow storing the files in git, showing them in this non-commercial demo, and making resized WebP and AVIF derivatives, with attribution. Images whose license forbids derivatives are not eligible. The code license does not cover those files.

## Roles

The product has three roles. There is no product admin screen.

| Action | Guest | Member | Leader |
| --- | --- | --- | --- |
| View landing, showcase, announcements, feed, visible post, visible comments, public profile, open theme | yes | yes | yes |
| Like, comment, upload, submit, vote | sign-in required | yes | yes |
| Edit and delete own caption, comment, and post | no | yes | yes |
| Edit own profile | no | yes | yes |
| One submission and one changeable vote on the open theme | no | yes | yes |
| Create, edit, and close a theme | no | no | yes |
| Hide and restore posts and comments | no | no | yes |
| See hidden posts and comments | no | own only | yes |
| Edit showcase and announcements, read theme stats | no | no | yes |

A guest is signed out. A hidden post or comment is absent for them. A direct link returns not found.

A member is a signed-in account. A second submission to the same theme is rejected. Their own hidden content remains visible to them.

A leader is a member with `Profile.is_leader`. A second open theme returns 409. The leader flag cannot be set through the product API. This role does not enter the Django admin.

The operator is not a circle role. `is_staff` on the Django user is the operator. Only the operator sets `is_leader`. The operator password exists only in Railway variables and in the local `.env`.

## Scenarios

A reviewer without a password walks the guest path. Member and leader paths are shown in screenshots and tests. Signing in to React and signing in to the panel are separate: each frontend has its own cookie.

### Guest

The guest opens the landing page and sees the showcase, announcements, and links to profiles and to the application. On Astro they open a public profile: name, bio, avatar, and visible posts. In React they scroll the feed and open a post: image, caption, EXIF, like count, and comments. Like, comment, upload, submission, and vote lead to sign-in. Hidden posts and comments are not on screen. A direct link to them says not found.

### Member

The member registers with username, email, and password and lands in the feed already signed in, or signs in to an existing account. They upload a JPEG, PNG, or WebP. Before the request, the form may show EXIF read in the browser. After save, the post is at the top of the feed and on their profile, with server EXIF, width, and height. A like changes immediately and rolls back if the request fails. They write a comment and a reply. A reply to a reply sits under the root comment. They edit their caption and their comment, delete their comment and their post, and edit their name, bio, and avatar. On the open theme they submit one of their existing posts, cast one vote, may change it, and may withdraw the submission. A second submission is rejected.

### Leader

In React the leader acts as a member. They open the panel separately and sign in there again. They create a theme with a title, a description, a start, and an end. It becomes the only open theme. They see submissions, including a submission whose post is hidden. Hiding a post removes it from the feed, from public submission lists, and from voting for everyone else. Restoring the post brings it back. They hide and restore a comment. Replies under it stay. They read the summary: submission count, vote count, and participant count. They may cast or change their one vote in the panel. They close the theme. New submissions and votes stop. They change the showcase order and create or edit an announcement. The landing home cache is purged.

The operator is outside these scenarios. They only set the leader flag in the Django admin.

## Domain model

The user stays the standard Django user: username, email, password, and `is_staff` for the operator only. Username length is 5–30 characters. Email is required and unique. The allowed username characters are the Django allauth default.

**Profile.** One-to-one with the user. Display name up to 50 characters, bio up to 500, avatar, and `is_leader`. An empty display name is shown as the username.

**Post.** Author, caption up to 2000 characters, a required image, master width and height, EXIF, file hash, status `visible` or `hidden`, and timestamps. Stored EXIF fields are camera, lens, focal length, aperture, shutter speed, ISO, and the time the photo was taken. GPS is not stored. The same hash from the same author returns a conflict. The public identifier is the numeric `id`. The slug is a readable address: taken from the caption, or from the `id` when the caption is empty, unique for that date. The author and the leader can see a hidden post.

**Comment.** Post, author, text up to 1000 characters, status, timestamps, and an optional `parent`. The parent is a root comment on the same post. A reply to a reply is stored with the root as parent. There is no deeper level. The author and the leader can see a hidden comment. Replies under it remain.

**Like.** User and post. The pair is unique.

**Challenge.** Title, description, start, end, status `draft`, `open`, or `closed`, and the creator. At most one challenge is open.

**Submission.** Challenge and post. The pair is unique. The submission author is the post author. A member has at most one submission on a challenge. A hidden post drops out of public lists and out of the totals. The submission row stays and returns with the post.

**Vote.** User, challenge, and submission. The submission belongs to that challenge. A member has one vote row on a challenge. Changing the vote updates the submission on that row. A vote for a hidden submission stays out of the summary until the post is visible again. Withdrawing a submission deletes that submission and the votes that pointed at it.

**Announcement.** Title, body, publication time, and author.

**FeaturedWork.** Post and showcase order. The leader replaces the whole set.

**RefreshToken.** A service row: hash of a random string, user, and expiry. The string itself lives only in the cookie. Sign-out deletes the hash.

Statistics are not stored. They are counted from visible submissions, votes that are currently included, and participants who have such a submission or such a vote.

## API contract

The base prefix is `/api`. The browser calls it on its own frontend. Vercel proxies the request to Railway. The SDK schema is `/api/schema/`. `GET /api/health` requires no authentication and reports only that the process is up.

### Session

`POST /auth/register` accepts username, email, and password. `POST /auth/login` accepts username or email, plus password. The response body contains an access token that lives for 15 minutes. The refresh cookie is `pk_refresh`, `HttpOnly`, `Secure`, `SameSite=Lax`, path `/api/auth`. `POST /auth/refresh` reads the cookie, revokes the old hash, and issues a new pair. `POST /auth/logout` deletes the hash and clears the cookie. `GET /auth/me` returns the user and the profile.

Local browsers open the apps on localhost, which they treat as a trustworthy origin, so the `Secure` cookie is set there as well.

### Errors

Every error body is one object: `code`, `message`, `fields`. Codes: `validation_error` 400, `not_authenticated` 401, `permission_denied` 403, `not_found` 404, `conflict` 409, `too_many_requests` 429. A hidden post or comment that the caller must not see is 404. A second open theme, a second submission to the same theme, and the same file hash from the same author are 409.

### Lists

The feed, profile posts, root comments, and theme submissions use an opaque cursor over `created_at` and `id`, newest first. The response is `results`, `next_cursor`, and `has_next`. The default limit is 20 and the maximum is 50. Query parameters are `cursor` and `limit`. Replies are nested inside their root comment. The showcase and announcements are returned in full.

`GET /posts?status=hidden` is leader-only and uses the same cursor. Without that parameter, hidden posts stay out. `GET /challenges/{id}/submissions` includes hidden submissions, marked as hidden, when the caller is the leader. For everyone else those submissions stay out.

### Profiles and posts

`GET /profiles/{username}`, `PATCH /profiles/me` (including the avatar), and `GET /profiles/{username}/posts`. `GET /posts`, `POST /posts` as one multipart request, `GET /posts/{id}`, `PATCH /posts/{id}` changes only the caption, and `DELETE /posts/{id}` deletes the author's post together with its likes, comments, submission, and votes for that submission. `POST /posts/{id}/hide` and `POST /posts/{id}/restore` are for the leader. Status cannot be changed through ordinary `PATCH`. A post payload includes width, height, EXIF, derivatives, `likes_count`, and `liked_by_me`.

EXIF shape:

```json
{
  "camera": "string or null",
  "lens": "string or null",
  "focal_length_mm": "number or null",
  "aperture": "number or null",
  "shutter_speed": "string or null",
  "iso": "number or null",
  "taken_at": "ISO-8601 string or null"
}
```

Each derivative is `{ "format": "webp" or "avif", "width": 480 or 960 or 1600, "url": "string" }`.

### Comments and likes

`GET` and `POST /posts/{id}/comments`. Create accepts an optional `parent_id`. When `parent_id` points at a reply, the API stores the root comment of that reply. The parent must belong to the same post. `PATCH` and `DELETE /comments/{id}` are the author. `POST /comments/{id}/hide` and `/restore` are the leader. Likes are `PUT /posts/{id}/like` and `DELETE /posts/{id}/like`.

### Theme

`GET /challenges/current`, `GET /challenges/{id}`, `POST /challenges`, `PATCH /challenges/{id}`, and `POST /challenges/{id}/close`. `POST /challenges` opens the theme. A body with `status: draft` saves it without opening. Opening a theme while another is open returns 409. `GET` and `POST /challenges/{id}/submissions` with `post_id`. `DELETE /challenges/{id}/submissions/{submission_id}` withdraws the author's submission. `POST /challenges/{id}/votes` with `submission_id` sets or replaces the vote. `GET /challenges/{id}/stats` is for the leader and returns `submissions_count`, `votes_count`, and `participants_count`.

### Landing content

`GET`, `POST`, `PATCH`, and `DELETE` for `/announcements`. `GET /featured` and `PUT /featured`. The PUT body replaces the ordered post list. Writes to the showcase and to announcements are leader-only.

### Limits

Sign-in and registration: 5 requests a minute per IP. Upload: 10 an hour per user. Writes: 60 a minute per user. Reads: 120 a minute per user.

## Architecture and monorepo

One repository. pnpm manages packages. Turborepo orders tasks. The current Django project moves to `apps/api`.

```text
apps/api        Django, DRF, OpenAPI
apps/web        React, Vite, React Router
apps/landing    Astro
apps/admin      Vue 3, Vite
packages/ui     SCSS/BEM, thin components, Storybook
packages/sdk    client generated from OpenAPI
docs/specs      this spec and later feature specs
```

`packages/sdk` is committed. A generate command rewrites it when `/api/schema/` changes. Frontends import the SDK. Shared ESLint, Prettier, and the base tsconfig live at the root. Apps extend them. Stylelint checks SCSS. Ruff checks Python. Pull request titles are Conventional Commits, checked by commitlint.

On the day the monorepo is created, every dependency is written as an exact version. Ranges `^`, `~`, and `*` are not used. The root `.npmrc` sets `save-exact=true`. `pnpm-lock.yaml` is committed. Python dependencies in `apps/api/requirements.txt` use `==`. Docker base images use the exact Node 22 and Python 3.12 patch tags available that day, not `latest`. A later upgrade is its own commit.

Runtime pins for the platform are Node 22, Python 3.12, and Django 5.1, at the exact patch chosen that day. The database is Postgres. Files are MinIO locally and an S3-compatible bucket on Railway. SQLite stays only in the current starter and is not migrated forward.

Docker Compose runs the API, Postgres, and MinIO. Frontends run through `pnpm dev` on the host so hot reload stays. Ports: API `8000`, Postgres `5432`, MinIO `9000`, web `5173`, admin `5174`, landing `4321`. Secrets live in `.env`. The repository gets `.env.example` with empty values.

Vercel hosts three projects: web, landing, and admin. Each rewrites `/api` to Railway. The rewrite target is `API_PROXY_ORIGIN`. Preview builds use the staging API. Production builds use the production API. Railway has two environments. Each has its own Postgres and its own bucket.

Turbo runs `lint`, `test`, and `build`. `ui` and `sdk` build before the apps that depend on them.

Feature specs, written before a behavior or API change, live at `docs/specs/features/NNNN-name.md` in English: goal, roles, behavior, API, acceptance, tests. A small bugfix that does not change behavior does not get a new spec.

## Applications

### Web

`apps/web` is client-rendered React on Vite and React Router. Routes are split: `/` feed, `/posts/new` upload, `/posts/:id` post, `/profiles/:username` profile, `/profiles/me/edit` profile edit, `/challenges/current` submission and vote, `/login`, `/register`. The initial route is at most 150 KB gzip. Feed CLS is at most 0.1.

A guest can scroll the feed, open a post, and open a profile. Actions that need an account go to `/login`. TanStack Query holds server data. Zustand holds the access token, the upload draft, and dialog flags. Like, comment, reply, and vote change immediately and roll back on failure. Creating a post waits for the API, then refreshes the feed and the profile posts and clears the draft. Sign-out clears the cache and the token. On `401` the SDK refreshes the access token once and retries the request.

The feed is CSS multi-column masonry with `break-inside: avoid` on each card. There is no masonry JavaScript library. The feed container uses container queries. Column counts are 1, then 2, 3, and 4 at container widths `48rem`, `64rem`, and `80rem`. Each figure reserves space with `aspect-ratio`. The first screen loads immediately. The rest uses `loading="lazy"`. The upload form may show EXIF from the file before the request. After the response, the card shows server EXIF and derivatives.

### Landing

`apps/landing` is Astro. The home page is static: showcase, announcements, and links to profiles and to web. Demo account profiles are static too. A profile created after deploy is rendered on request and cached for about 60 seconds. Changing the showcase or an announcement purges the home cache immediately. The build calls the SDK. There is no client Query cache and no Zustand. There is no client Sentry SDK.

Mobile Lighthouse on these pages is at least 95. LCP is at most 2.5 s, CLS at most 0.1, TBT at most 200 ms, and INP at most 200 ms. JavaScript is at most 30 KB gzip. The page is static. One small island is allowed only for a menu. The first showcase image uses `fetchpriority="high"` and preload. The rest are lazy. `lang="ru"`. The text column is at most `72ch`.

### Admin

`apps/admin` is Vue 3 on Vite, client-rendered. Routes are split: `/login`, `/challenge`, `/moderation`, `/stats`. The initial route is at most 150 KB gzip. The panel is outside the Lighthouse 95 target. Server data uses `@tanstack/vue-query`. The token and dialog flags live in a composable. Sign-in is separate from React because this frontend has its own cookie.

On `/challenge` the leader creates and edits the theme, closes it, sees submissions including hidden posts, and casts or changes their one vote. On `/moderation` they hide visible posts and restore hidden ones, and do the same for comments on an open post. On `/stats` they see submission, vote, and participant counts. An account that is not the leader receives `403` from the API.

### UI kit

`packages/ui` is authored only in `.scss`. Public tokens are custom properties emitted once from an SCSS map. Components read `var(--pk-*)`. SCSS variables are not a public API. Nesting, `@use`, and `@forward` stay in SCSS. `@import` is not used. One block is one file. The prefix is `pk-`: `pk-button`, `pk-button__label`, `pk-button--primary`. An element of an element is not named with a second `__`. Styles compile to one file. Thin React, Vue, and Astro components apply the same classes. Storybook shows the React versions. The post card, the comment thread, and the submission row live in the apps.

Sizes are `rem`. Inside a component that should follow its own font size, use `em`. Pixels remain for hairlines such as a `1px` border. Component layout and the feed columns use container queries. A viewport media query is allowed on the page shell, where a container does not exist yet.

Base colors are `oklch` with lightness as a number from 0 to 1. Derived states use CSS relative color syntax. The browser calculates the channels. SCSS only writes the declarations.

```scss
:root {
  --pk-color-bg: oklch(0.9679 0.005 78.3);
  --pk-color-surface: oklch(1 0 0);
  --pk-color-text: oklch(0.2178 0 0);
  --pk-color-accent: oklch(0.4698 0.143 37.3);

  --pk-color-accent-hover: oklch(from var(--pk-color-accent) calc(l + 0.06) c h);
  --pk-color-text-muted: oklch(from var(--pk-color-text) 0.4628 c h);
  --pk-color-border: oklch(from var(--pk-color-text) 0.6 c h);
}
```

Hover, active, muted text, and borders are derived from an existing token with relative color syntax. There is no second independent palette. Muted text replaces the `l` channel. It does not use alpha, so it stays at or above 4.5:1 on the page background. Alpha from the origin color is for overlays, not for body text. The input border replaces `l` so the boundary stays at or above 3:1 on the surface. The focus ring uses the accent. The target is current evergreen browsers. There is no stylesheet branch for older engines.

The type stack is `system-ui, sans-serif`. No web font file is loaded. The spacing steps are 0.25, 0.5, 0.75, 1, 1.5, 2, and 3 rem. Control radius is 0.25 rem. Photo radius is 0. Container thresholds for the feed are `48rem`, `64rem`, and `80rem`.

The kit contains `Button`, `IconButton`, `Input`, `Textarea`, `Field`, `Avatar`, `Dialog`, `Tabs`, `Badge`, `Spinner`, and `Skeleton`. A dialog traps focus. Tabs and buttons work from the keyboard. Focus is visible.

Both web and landing, and the admin panel, take their look from this package.

### SDK

`packages/sdk` is generated from `/api/schema/` by `openapi-typescript` at an exact version pinned on the day the package is created. Generated types are committed. A handwritten client in the same package performs fetch, attaches the access token, and on `401` calls refresh once and retries. That handwritten client is tested. Public landing reads send no token. Dependency versions in the package are exact.

### API

`apps/api` is Django 5.1 and Django REST framework. The `feed` app goes away. The feed is `GET /posts`. The areas are auth and profile, posts with comments and likes, themes, and showcase with announcements. Allauth still requires an email and a unique email. Email confirmation does not block sign-in. drf-spectacular serves OpenAPI. Upload checks the file, writes EXIF without GPS, builds the master and the derivatives, and stores them in MinIO or the bucket. The seed command is idempotent. Logs are JSON on stdout. Sentry is enabled for the API.

## Data and cache

TanStack Query in React and Vue stores server data. Keys are `['me']`, `['posts', 'feed']`, `['posts', 'hidden']`, `['posts', id]`, `['profiles', username]`, `['profiles', username, 'posts']`, `['posts', id, 'comments']`, `['challenges', 'current']`, `['challenges', id, 'submissions']`, `['challenges', id, 'stats']`, `['announcements']`, and `['featured']`. Cursor lists are infinite queries.

Like, comment, reply, and vote change patch every cached copy of that entity in `onMutate` and roll back on error. A temporary comment is replaced by the server payload. Creating a post waits for the response, then invalidates the feed and the profile posts. Hiding a post removes it from guest lists and marks it in the leader list. Sign-out clears the query cache and the token. `401` causes one refresh and one retry.

In React, Zustand holds the access token, the upload draft (file, local EXIF, caption, progress), and dialog flags. In Vue a composable holds the token and the flags. Astro calls the SDK at build time and keeps no client cache.

## Images

Accepted types are JPEG, PNG, and WebP, up to 10 MB and 40 megapixels. The type is detected from the file contents. The master is stored with its long edge at most 2560. Derivatives are widths 480, 960, and 1600 in WebP and AVIF. EXIF is removed from derivative files. The database keeps camera, lens, focal length, aperture, shutter speed, ISO, and the capture time. GPS is not written. The same SHA-256 from the same author returns `409`. Local files live in MinIO. Railway uses an S3-compatible bucket. The response includes width, height, and derivatives. Layout reserves the frame with `aspect-ratio`. Below the first screen, images use `loading="lazy"`. If the API image has no libvips, the upload test fails.

## Performance

On the Astro home page and the static demo profiles, mobile Lighthouse is at least 95: LCP at most 2.5 s, CLS at most 0.1, TBT at most 200 ms, INP at most 200 ms, and landing JavaScript at most 30 KB gzip. The first showcase image is preloaded. React and Vue initial routes are at most 150 KB gzip. Other routes load separately. CI checks these budgets. React, Vue, and a cold Railway start are outside the 95 target.

## Accessibility

The interface is Russian. `lang="ru"`. The target is WCAG 2.2 AA. Text contrast is at least 4.5:1. Large text and boundaries are at least 3:1. Focus is visible. Fields have labels. A field error is tied to its field. A dialog keeps focus inside. Buttons and tabs work from the keyboard. A photo's caption becomes `alt`. An empty caption becomes `Фото {name}`. Primary controls are at least `2.75rem`. Small controls are at least `1.5rem`. Animations stop under `prefers-reduced-motion`. The landing text column is at most `72ch`. Page shell padding is `1rem`, and `1.5rem` from a shell width of `48rem`.

## Testing

Handwritten code starts with a failing test. The 90% line gate is computed twice: handwritten TypeScript, and handwritten Python. Generated SDK output, migrations, and config files are outside both counts. There is no single percentage for the whole repository.

Vitest and Testing Library cover components, SDK error parsing, and cache updates for like, comment, reply, vote change, and rollback. Pytest covers permissions, validation, the cursor, the single open theme, vote replacement, submission withdrawal, and the image pipeline, including the failure when libvips is missing.

Playwright runs every screen against the built apps and the Compose API. Passwords for `anya` and `kirill` come from CI environment variables and are not written in the repository.

- Astro: home and public profile.
- React: sign-in, registration, feed, post, profile, upload, submission, and vote.
- Vue: weekly theme, moderation, and statistics.

There are no screenshot baseline tests. Component accessibility is checked in Testing Library through name, role, and dialog focus.

## CI/CD and deploy

On a pull request, GitHub Actions runs lint, typecheck, tests with the coverage gate, build, Playwright, and mobile Lighthouse for the home page and one static demo profile. commitlint checks the pull request title. Secrets live in GitHub Actions, Vercel, and Railway. The repository contains `.env.example` with empty values.

Three Vercel projects: web, landing, and admin. Each rewrites `/api` to Railway. Preview points at staging. Production builds point at production. Railway has two environments, each with its own Postgres and bucket. API deploy runs migrate. The seed is manual and idempotent. It does not run on every deploy.

CI uploads source maps to Sentry for React, Vue, and Django. Sentry has separate staging and production environments. The landing page has no client SDK. The API image and base images are pinned to exact versions, not `latest`.

## Security

The browser calls `/api` on its own frontend. Vercel proxies to Railway, so the cookie is first-party: `HttpOnly`, `Secure`, `SameSite=Lax`. There is no credentialed CORS allowlist. The access token is a JWT for 15 minutes and stays in memory. The refresh value is a random string in the cookie. The database stores only its hash. Refresh revokes the old hash and issues a new one. Sign-out deletes the hash.

Limits are those in the API contract. Over the limit the response is `429`.

The file is checked by content, not by extension: JPEG, PNG, or WebP, up to 10 MB and 40 megapixels. Caption, comment, bio, and display name limits are enforced by the API. Browser checks do not replace them.

A hidden post and a hidden comment are 404 for callers who must not see them. Only a leader can hide and restore. Only the operator can set the leader flag, and only in the Django admin. Ordinary `PATCH` cannot change status. Logs omit the request body, cookies, and the `Authorization` header.

## Demo and packaging

The seed has four authors: `anya`, `kirill`, `nina`, and `mark`. Passwords for `anya` and `kirill` come from Railway environment variables and from the local `.env`. `nina` and `mark` cannot sign in. The README and the interface say nothing about passwords.

The seed creates 24 photos, comments, likes, one open theme with submissions and votes, 6 showcase works, and 2 announcements. Photos are spread across the four authors so each profile has posts. Images go through the normal pipeline. The seed fills card EXIF when the file has none. The four profiles are built statically. Running the seed again does not duplicate rows. It does not run on every deploy.

The frames are small JPEGs in `apps/api/fixtures/photos/`. Their license allows git storage, display in this non-commercial demo, and WebP and AVIF derivatives. `CREDITS.md` beside them names the author and the license of each file. Images that forbid derivatives are not added. The seed does not download anything. Replacing the files does not require a seed code change. Seed copy shown in the product is Russian.

The README is Russian. The top has two or three English sentences: what this is and which apps it contains. Then the live landing, application, and panel URLs, four screenshots of the finished interface (showcase, feed, post with EXIF and comments, theme panel), a Mermaid diagram, and the local Docker Compose start. Badges: GitHub Actions status, the coverage gate, and landing Lighthouse. The code license is PolyForm Strict 1.0.0, copyright Aleksey Kerkin, 2024–2026.

The diagram shows the browser, the three Vercel frontends, the `/api` proxy, Railway, Postgres, the bucket, and the `ui` and `sdk` packages.

## MVP stages and later work

The MVP is the whole product in this spec. The stages are the build order. The next stage starts when the previous one works.

1. **Foundation.** Monorepo, exact versions, Compose with API, Postgres, and MinIO, Django moved to `apps/api`, session, the error format, `/api/schema/`, empty frontend and package shells, `LICENSE` replaced with PolyForm Strict, and the first CI.
2. **React core.** Feed, post, upload, EXIF, likes, comments, profiles, submission, and vote. The API and SDK for those screens. Optimistic updates.
3. **UI kit.** SCSS tokens and components, Storybook, and web switched onto the shared classes.
4. **Astro.** Home, showcase, announcements, static demo profiles, cache for new profiles, and the Lighthouse gate.
5. **Vue.** Theme, moderation, statistics, and editing the showcase and announcements.
6. **Packaging.** Seed, README, screenshots, diagram, badges, staging, and production.

Follows, messages, search, social login, realtime, mobile apps, a language switch, payments, and a dark theme are not in these stages. They need a new spec.

The decisions themselves live in this spec.

## Risks

The volume is large, so a stage does not start until the previous one works. If the leader password leaks, a stranger can hide posts and change the theme. The recovery is a manual reseed. That role cannot open the Django admin.

Lighthouse depends on the weight of the first showcase image. Derivatives, preload, and the CI check keep the budget from slipping quietly. The three UI kit wrappers stay aligned through shared SCSS classes, Storybook, and component tests. Missing libvips fails the upload test. Demo JPEGs can be replaced in the seed folder. A cold Railway start can make the React app slower. That app is outside the Lighthouse gate.

## Glossary

**Guest.** Signed out.

**Member.** An ordinary account.

**Leader.** A member with `is_leader`.

**Operator.** `is_staff`. Django admin only.

**Theme.** A challenge. At most one is open.

**Submission.** A post the author sent to a theme.

**Vote.** One chosen submission. It can be changed while the theme is open.

**Showcase.** The ordered posts on the landing page.

**Announcement.** A short news item on the home page.

**Master.** The stored original whose long edge is at most 2560 px.

**Derivative.** A WebP or AVIF at width 480, 960, or 1600.

**Cursor.** An opaque continuation of a list.

**Access token.** A short JWT kept in memory.

**Refresh token.** A random string in the cookie. The database stores only its hash.
