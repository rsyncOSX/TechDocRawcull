# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Repo Is

Technical documentation site for **RawCull**, a native macOS photo culling app for Sony ARW RAW files. Built with Hugo + Docsy theme, deployed to Netlify. The `sourcecode/RawCull/` tree contains actual Swift source files from the app — they are included here to be referenced by documentation pages, not compiled by this repo.

## Commands

```bash
# Install dependencies
npm install

# Local development server (http://localhost:1313)
npm run serve

# Production build
npm run build:production

# Preview build (with Netlify deploy URL)
npm run build:preview

# Link checking
npm run test

# Clean build artifacts
npm run clean
```

Hugo Extended v0.160.1 is required (installed via npm devDependencies as `hugo-extended`).

### Docker alternative

```bash
docker-compose up
```

Serves on port 1313.

## Architecture

### Hugo Site Layout

- `content/en/docs/` — Markdown documentation pages (the primary content to edit)
- `content/en/_index.md` — Homepage
- `layouts/` — Custom Hugo layout overrides on top of Docsy theme
- `assets/scss/` — SCSS stylesheet customizations
- `static/` — Static assets served as-is
- `hugo.yaml` — Main Hugo configuration (base URL, Docsy module import, syntax highlighting, Mermaid support)
- `config.yaml` — Hugo version constraint check

The Docsy theme is pulled as a **Hugo module** (`go.mod`/`go.sum`). To work on Docsy itself locally, use `docsy.work` (Hugo workspace file).

### Documentation Content

Each page in `content/en/docs/` covers a distinct architectural topic of the RawCull app:

| File | Topic |
|------|-------|
| `_index.md` | Overview, system requirements, supported camera bodies |
| `compile.md` | Building RawCull: Xcode, code signing, notarization |
| `scanpipeline.md` | File discovery and scan pipeline |
| `concurrency.md` | Concurrency: patterns, actors, cancellation, GCD bridging, all flows |
| `cache.md` | Three-layer cache (memory → disk → source decode) |
| `sharpnessscoring.md` | Image sharpness analysis algorithms |
| `sonymakernoteparser.md` | Sony proprietary EXIF/MakerNote parsing |
| `thumbnail.md` | Thumbnail generation and caching strategies |
| `security.md` | Sandboxing and privacy |
| `savedfiles.md` | Saved file management |
| `heavy.md` | Heavy computation patterns |

Pages may embed code blocks referencing files from `sourcecode/RawCull/`.

### Swift Source Tree (`sourcecode/RawCull/`)

Organized to mirror the actual macOS app's Xcode project:

- `Actors/` — Swift concurrency actors (thread-safe concurrent operations): scanning, caching, thumbnail loading
- `Views/` — SwiftUI view hierarchy (~20 subdirectories)
- `Model/` — Data models, ViewModels (MVVM), handlers, RAW file representations
- `Enum/` — Sony ARW extraction, MakerNote parser, file type support
- `Extensions/` — Swift extensions
- `Kernels.ci.metal` — Metal GPU compute kernel for image processing

### Deployment

Netlify auto-deploys from `main`. Build settings are in `netlify.toml`:
- Production: `npm run build:production` → `public/`
- Previews: `npm run build:preview` (injects Netlify deploy URL as base URL)
- Go 1.23.2, Node version from `.nvmrc`

Dependabot runs daily to update npm and bundler dependencies (max 10 open PRs per ecosystem).
