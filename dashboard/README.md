# Liverpool tactical dashboard

Static React/Vite presentation for the repository's committed squad, fixture,
manager-prior, player-profile, and posterior JSON.

## Local commands

```bash
npm ci --ignore-scripts
npm run dev
npm run lint
npm run build
npm run preview
```

`predev` and `prebuild` run `scripts/sync-data.mjs`, which replaces the ignored
`public/data/` directory with a copy of the repository's committed project data.
The production build is written to ignored `dist/`.

## Deployment

The production base path is `/liverpool-tactical-bayesian/` for the repository's
GitHub Pages project site. `.github/workflows/deploy-pages.yml` validates the
model/data, lints and builds the dashboard, uploads `dist/`, and deploys it with
the official Pages actions.

Do not edit `public/data/` or `dist/` directly; both are reproducible artifacts.
