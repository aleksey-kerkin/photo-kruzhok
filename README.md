# Фото-кружок

Photo Kruzhok is a portfolio monorepo for a live photo-club demo. It contains a Django API, one Astro site with Vue islands, and shared `ui` and `sdk` packages.

[![CI](https://github.com/aleksey-kerkin/photo-kruzhok/actions/workflows/ci.yml/badge.svg)](https://github.com/aleksey-kerkin/photo-kruzhok/actions/workflows/ci.yml)
[![coverage](https://img.shields.io/badge/coverage-gate-in%20CI-blue)](https://github.com/aleksey-kerkin/photo-kruzhok/actions/workflows/ci.yml)
[![lighthouse](https://img.shields.io/badge/lighthouse-web%20gate-in%20CI-blue)](https://github.com/aleksey-kerkin/photo-kruzhok/actions/workflows/ci.yml)

## Приложения

| Приложение | Локальный адрес |
| --- | --- |
| Сайт (сетка, посты, вход, панель) | http://localhost:4321 |
| API | http://127.0.0.1:8000 |

Репозиторий: `git@github.com:aleksey-kerkin/photo-kruzhok.git`

## Скриншоты

Витрина:

![Витрина](docs/screenshots/showcase.png)

Сетка фото:

![Сетка](docs/screenshots/feed.png)

Пост с EXIF и комментариями:

![Пост](docs/screenshots/post-exif-comments.png)

Панель темы:

![Панель темы](docs/screenshots/theme-panel.png)

## Архитектура

```mermaid
flowchart LR
  browser[Браузер]
  web[Astro site]
  proxy["/api proxy"]
  railway[Railway API]
  pg[(Postgres)]
  bucket[(Bucket)]
  ui[packages/ui]
  sdk[packages/sdk]

  browser --> web
  web --> proxy
  proxy --> railway
  railway --> pg
  railway --> bucket
  web -.-> ui
  web -.-> sdk
```

## Локальный запуск

API, Postgres и MinIO поднимаются через Docker Compose. Сайт запускается на хосте:

```bash
docker compose up -d
pnpm --filter @photo-kruzhok/web dev
```

Порты: API `8000`, Postgres `5432`, MinIO `9000`, сайт `4321`. Секреты лежат в `.env` (шаблон — `.env.example`).

## Лицензия

Код распространяется по [PolyForm Strict License 1.0.0](LICENSE). Copyright © Aleksey Kerkin, 2024–2026.
