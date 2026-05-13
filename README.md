# DocLens — AI Document Scanner + Smart Summary + Instant Translate

> One camera flow. Three AI superpowers. Zero friction.

---

## Table of Contents

- [1. Product Overview](#1-product-overview)
- [2. Architecture](#2-architecture)
- [3. Routes & Navigation](#3-routes--navigation)
- [4. Project Structure](#4-project-structure)
- [5. Theme & Design System](#5-theme--design-system)
- [6. State Management](#6-state-management)
- [7. Service Layer](#7-service-layer)
- [8. Views (Detailed)](#8-views-detailed)
- [9. Components (Detailed)](#9-components-detailed)
- [10. Gateway Integration](#10-gateway-integration)
- [11. Monetization](#11-monetization)
- [12. Play Store Deployment](#12-play-store-deployment)
- [13. ASO Keywords](#13-aso-keywords)
- [14. Development Phases](#14-development-phases)
- [Appendix A: Flet Patterns Catalog](#appendix-a-flet-patterns-catalog)

---

## 1. Product Overview

### What It Does

DocLens is a single-app trifecta:

| Feature | Trigger | AI Route | Output |
|---|---|---|---|
| **Smart Scanner** | Camera or gallery | `multimodal` | Clean, straightened, enhanced document image |
| **AI Summary** | One tap after scan | `multimodal` → `text` | Bullet-point tl;dr of document contents |
| **Smart Translate** | One tap after scan | `multimodal` → `text` | Document text in user's chosen language |

All three share the same camera/gallery entry point — no separate flows.

### Why This Wins

- **Shared funnel**: One camera flow feeds all 3 features — minimal code, maximum value.
- **Daily use**: People scan documents every day = ad impressions compound.
- **AI is the unlock**: Most scanner apps have OCR. Almost none have AI summary + translate in one tap. Adobe Scan just added "Generative summary" in 2025 and it propelled them to #5 grossing in the Business category.
- **Proven market**: CamScanner ($5.6M/mo), Adobe Scan (#5 grossing Business), TapScanner (#2 grossing in Brazil), iScanner (125M+ users). The scanner category is validated.
- **Keyword density**: "AI scanner", "document scanner", "translate PDF", "PDF scanner AI" are all high-volume ASO terms.

### Target Users

- Students (scan notes, get summaries, translate foreign texts)
- Business professionals (scan contracts, get AI briefs)
- Travelers (scan signs/menus, translate instantly)
- Remote workers (scan whiteboards, digitize documents)

---

## 2. Architecture

### Data Flow

```
User taps Camera (or Gallery)
        │
        ▼
CameraViewfinder (overlay)  or  FilePicker
        │
        ▼
Image bytes captured
        │
        ▼
Preview in Scan Result view
        ├── "AI Summary" → POST /chat {task_type: "multimodal", image: base64}
        │                         → response: text description
        │                         → POST /chat {task_type: "text", "Summarize this..."}
        │                         → response: bullet-point summary
        │
        ├── "Translate"  → POST /chat {task_type: "multimodal", image: base64}
        │                         → response: extracted text
        │                         → POST /chat {task_type: "text", "Translate to X..."}
        │                         → response: translated text
        │
        └── "Save PDF"   → Generate PDF from image → Export / Share
```

### Key Design Decisions

- **No local database** — scan history is displayed ephemerally in-session. Users can save PDFs to device storage. This keeps the app simple and avoids Play Store data-deletion policy complexity.
- **Local-only credits** — daily scan limit stored in `flet-secure-storage` (pattern from Spaninsight's `CreditService`). No backend needed.
- **AI calls go through `kiri-gateway`** — every app uses the same gateway. Gateway handles fallback chains, multi-key rotation, auth.
- **Camera and gallery share same callback** — same `on_image_captured(data, mime, filename)` handler regardless of source. This keeps the scan result view identical whether the image came from camera or file picker.

---

## 3. Routes & Navigation

```
/splash     → Logo + loading bar (1.5s then go)
/scan       → Main camera viewfinder OR image picker trigger
/result     → Shows captured image + action buttons (Summary, Translate, Save PDF)
/summary    → Streaming AI summary display with markdown rendering
/translate  → Language picker → streaming translation display
/settings   → Theme toggle, credit info, about, ad banner
```

### Route Change Handler Pattern

```python
async def route_change(e=None):
    page.views.clear()
    if page.route == "/splash":
        page.views.append(build_splash_view(page, navigate))
    elif page.route == "/scan":
        page.views.append(build_scan_view(page, navigate, on_captured))
    elif page.route == "/result":
        page.views.append(build_result_view(page, navigate, captured_image))
    elif page.route == "/summary":
        page.views.append(build_summary_view(page, navigate, captured_image))
    elif page.route == "/translate":
        page.views.append(build_translate_view(page, navigate, captured_image))
    elif page.route == "/settings":
        page.views.append(build_settings_view(page, navigate))
    page.update()

page.on_route_change = route_change
```

Navigation uses `page.route = route` + `await route_change()` pattern (same as Spaninsight/Akili). Back button = `view_pop` handler.

---

## 4. Project Structure

```
DocLens/
├── pyproject.toml          # Build config, dependencies, permissions
├── src/
│   ├── main.py             # Entry: page config, routing, services bootstrap
│   ├── core/
│   │   ├── __init__.py
│   │   ├── state.py        # @ft.observable AppState singleton
│   │   ├── theme.py        # M3 color palette + gradient builders
│   │   ├── tokens.py       # Spacing, radius, font size, icon size constants
│   │   ├── styles.py       # Reusable widget factories (glass_card, setting_tile, appbar)
│   │   └── constants.py    # API URL, secrets, limits, ad unit IDs
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py   # Calls kiri-gateway /chat (text + multimodal)
│   │   ├── camera.py       # flet-camera wrapper (from FletBot pattern)
│   │   ├── file_picker.py  # ft.FilePicker wrapper (from FletBot/Akili pattern)
│   │   ├── ad_service.py   # flet-ads wrapper (from KTV/spaninsight pattern)
│   │   ├── credit_service.py # Local daily scan limit (from Spaninsight pattern)
│   │   └── share.py        # Clipboard + share sheet (from FletBot pattern)
│   ├── views/
│   │   ├── __init__.py
│   │   ├── splash.py       # Splash screen
│   │   ├── scan.py         # Camera / gallery picker
│   │   ├── result.py       # Scan preview + action buttons
│   │   ├── summary.py      # AI summary (streaming markdown)
│   │   ├── translate.py    # Language picker + translation result
│   │   └── settings.py     # Preferences, credits, about
│   └── components/
│       ├── __init__.py
│       ├── camera_viewfinder.py  # Full-screen camera overlay (from FletBot pattern)
│       ├── media_preview.py      # Staged image preview (from FletBot pattern)
│       ├── action_button.py      # Reusable feature button (Summary/Translate/Save)
│       └── ad_banner.py          # Inline banner ad wrapper (from KTV pattern)
└── assets/
    ├── icon.png
    ├── logo.png
    └── languages.json     # Language list for translation picker
```

---

## 5. Theme & Design System

**Borrowed from FletBot + KTV Player patterns.**

### Colors (`core/theme.py`)

```python
# Brand — clean professional blue
PRIMARY = "#4A6CF7"          # Trustworthy blue
PRIMARY_DARK = "#3651D4"
ACCENT = "#00D9FF"           # Cyan accent for AI features

# Surfaces
DARK_BG = "#0F1118"
DARK_SURFACE = "#1A1D2E"
LIGHT_BG = "#F5F7FA"
LIGHT_SURFACE = "#FFFFFF"

# Semantic
SUCCESS = "#00E676"
WARNING = "#FFB74D"
ERROR = "#FF5252"
```

### Tokens (`core/tokens.py`)

Same pattern as `fletbot/src/theme/tokens.py` — `RADIUS_*`, `SPACE_*`, `FONT_*`, `ICON_*`, `ANIMATION_MS`, `BLUR_*` constants. Every magic number lives in one file.

### Styles (`core/styles.py`)

Reusable widget factories from FletBot's `theme/styles.py`:
- `glass_card(content, width, padding)` — frosted-glass container
- `standard_appbar(title, leading, actions)` — consistent AppBar
- `section_header(title)` — settings-style section label
- `setting_tile(icon, title, subtitle, trailing)` — settings row
- `primary_button(text, on_click)` — filled primary CTA
- `action_chip(icon, label, color, on_click)` — result view action button

### Typography

- Font: `Inter` from Google Fonts (same as Akili)
- Light mode / Dark mode both supported with theme toggle

---

## 6. State Management

Pattern from Spaninsight/Akili/KTV — `@ft.observable` singleton:

```python
@ft.observable
class AppState:
    # Scan
    current_image: bytes | None = None
    current_image_mime: str = ""
    current_image_name: str = ""

    # AI Results
    current_summary: str = ""
    current_translation: str = ""
    current_target_language: str = ""

    # UI
    is_loading: bool = False
    is_summarizing: bool = False
    is_translating: bool = False
    theme_mode: ft.ThemeMode = ft.ThemeMode.LIGHT

    # Credits (local-only, stored in SecureStorage)
    scans_today: int = 0
    daily_scan_limit: int = 5  # 5 free scans per day

    def clear_scan(self):
        self.current_image = None
        self.current_image_mime = ""
        self.current_image_name = ""
        self.current_summary = ""
        self.current_translation = ""

state = AppState()
```

---

## 7. Service Layer

### ai_service.py — Pattern from FletBot + Spaninsight

Makes HTTP calls to `kiri-gateway /chat`. Supports both streaming and non-streaming.

| Function | Task Type | Purpose |
|---|---|---|
| `check_health()` | — | Gateway health ping |
| `analyze_document(image_bytes, mime)` | `multimodal` | Extract text from document image |
| `summarize(text, stream_callback)` | `text` | Generate bullet-point summary |
| `translate(text, target_lang, stream_callback)` | `text` | Translate text to target language |

Uses `httpx.AsyncClient` with 30s timeout. Auth: `Authorization: Bearer <GATEWAY_SECRET>`.

### camera.py — Pattern from FletBot

```python
class CameraService:
    async def capture_photo() -> tuple[bytes, str] | None
        # Create Camera, add to overlay, initialize, take_picture, return (bytes, mime)
        # Clean up overlay after capture
```

Same code structure as `fletbot/src/services/camera.py`. Uses `flet_camera.Camera`, `ResolutionPreset.MEDIUM`.

### file_picker.py — Pattern from FletBot + Akili

```python
class FilePickerService:
    def pick_image(on_result: callable)
        # Trigger ft.FilePicker.pick_files(allowed_extensions=["png","jpg","jpeg","webp"], with_data=True)
        # on_result(bytes, mime, filename)
```

Same as `fletbot/src/services/file_picker.py` and `akili-app/src/services/file_picker.py`.

### ad_service.py — Pattern from KTV Player

KTV Player is the production app. Its `AdService` pattern:
- Preload interstitial on startup (`preload_interstitial`)
- Show interstitial at natural transitions
- Banner ads embedded between content
- Re-preload interstitial after close
- Platform check: `page.platform.is_mobile()`

DocLens will use live AdMob IDs from day 1 since we're targeting Play Store.

### credit_service.py — Pattern from Spaninsight

```python
class CreditService:
    async def initialize() -> int   # Load from SecureStorage, reset if new day
    async def can_scan() -> bool    # Check if under daily limit
    async def use_scan() -> bool    # Increment scan counter
    async def get_remaining() -> int
```

All local, no backend. Daily limit stored in `flet-secure-storage`. Premium users have unlimited.

### share.py — Pattern from FletBot

```python
class ShareService:
    async def copy_text(text: str)      # page.clipboard.set()
    async def share_text(text: str)     # Native share sheet
    async def save_pdf(image_bytes)     # Save to device storage
```

---

## 8. Views (Detailed)

### splash.py (`/splash`)

- Logo + app name + "AI Document Scanner" tagline
- Progress bar (1.5s duration)
- Check credit daily reset
- Navigate to `/scan` after splash
- Pattern: `ktv-player/src/views/splash.py`

### scan.py (`/scan`)

- Full-screen view with two large buttons:
  - **Take Photo** — opens `CameraViewfinder` overlay
  - **Choose from Gallery** — opens `FilePicker`
- Bottom banner ad
- Header with settings gear icon
- Pattern: FletBot's `_on_camera` + `_on_attach` handlers from `chat_view.py`

### result.py (`/result`)

- Shows captured image in large container with rounded corners
- Below image: three action buttons in a row:
  - **AI Summary** (sparkles icon) — navigates to `/summary`
  - **Translate** (language icon) — navigates to `/translate`
  - **Save PDF** (download icon) — saves to device, shows SnackBar
- Credit counter in top-right corner
- Bottom banner ad
- Back button (AppBar leading) to `/scan` for a new scan

### summary.py (`/summary`)

- AppBar: "AI Summary" with back button
- Sends image to gateway multimodal route, then text route for summarization
- Streaming response rendered in Markdown (pattern: FletBot's `MessageBubble` + `MarkdownRenderer`)
- While loading: `ProgressRing` + "AI is reading your document..."
- After complete: Copy button + Share button (pattern: FletBot `_copy_response` / `_share_response`)
- Banner ad at bottom

### translate.py (`/translate`)

- Step 1: Language picker (`ft.Dropdown` with common languages)
  - English, Spanish, French, German, Chinese, Japanese, Arabic, Portuguese, plus "Other..."
- Step 2: Sends image → gateway multimodal → extract text → gateway text → translate
- Step 3: Shows original extracted text + translated text side by side
- Both texts selectable and copyable
- "Swap languages" button

### settings.py (`/settings`)

- Pattern: `fletbot/src/views/settings_view.py`
- Section: **SCANNING**
  - Daily scans remaining (with progress bar)
  - Upgrade to Premium button
- Section: **APPEARANCE**
  - Theme toggle (Light/Dark)
- Section: **ABOUT**
  - Version
  - Kiri Gateway link
  - Privacy policy link
- Banner ad in middle of settings
- No sign-out needed (no accounts)

---

## 9. Components (Detailed)

### CameraViewfinder

Full-screen overlay. Pattern from `fletbot/src/components/camera_viewfinder.py` + `akili-app/src/components/camera_viewfinder.py`.

- `ft.Stack` with camera preview + capture button + close button + flip button
- Capture button: white circle with primary border, scale animation on tap
- Close button: top-right X icon
- Flip camera: visible when >1 camera available
- On capture: calls `on_capture(bytes, mime, filename)`, then closes itself

### MediaPreview

Shows selected image before navigating to result. Pattern from `fletbot/src/components/media_preview.py`.

- Image thumbnail with filename
- Remove button (X)
- Used in scan view to confirm image before processing

### ActionButton

Reusable CTA button for result view.

```python
ActionButton(icon="auto_awesome", label="AI Summary", color=PRIMARY, on_click)
```

- Container with icon + label
- Subtle background tint of the color
- Ripple effect on tap
- Scale animation on press

### AdBanner

Inline banner ad. Pattern from `ktv-player/src/services/ad_service.py`.

- Wraps `flet_ads.BannerAd` in a centered container
- Falls back to empty container on desktop/web
- Used in scan, result, summary, translate, and settings views

---

## 10. Gateway Integration

DocLens talks to `kiri-gateway` at `https://api.kiri.ng/chat`.

### Auth

Every request includes:
```
Authorization: Bearer <GATEWAY_SECRET>
Content-Type: application/json
```

### Task Types Used

| Task Type | When | Payload |
|---|---|---|
| `multimodal` | First call after scan | `{ messages: [{ role: "user", content: [{ type: "text", text: "Extract all text..." }, { type: "image_url", image_url: { url: "data:image/jpeg;base64,..." } }] }], task_type: "multimodal", stream: false }` |
| `text` | Summary generation | `{ messages: [{ role: "user", content: "Summarize this document text in 3-5 bullet points..." }], task_type: "text", stream: true }` |
| `text` | Translation | `{ messages: [{ role: "user", content: "Translate the following text to French..." }], task_type: "text", stream: true }` |

### Fallback Behavior

If the first multimodal model fails (llama-4-scout is down), the gateway automatically falls through to nemotron-3-nano-omni, then gemma-4. DocLens doesn't need to handle this — the gateway does it transparently. The `_kiri_model_used` tag in the response tells us which model actually served the request.

### constants.py

```python
API_BASE_URL = "https://api.kiri.ng"
API_CHAT_ENDPOINT = f"{API_BASE_URL}/chat"
GATEWAY_SECRET = "doclens-mobile-v1"
USER_AGENT = "DocLens/1.0.0"
```

---

## 11. Monetization

### Free Tier

- 5 document scans per day (resets daily like Spaninsight's credit system)
- Banner ads at bottom of every view
- Interstitial ad after every 3rd scan
- AI Summary and Translation included in free tier (to drive stickiness)
- Save PDF as image (no OCR-text PDF in free tier)

### Premium Tier ($4.99/month or $29.99/year)

- Unlimited scans per day
- No banner ads
- No interstitial ads
- OCR-text PDF export (searchable, selectable text in PDF)
- Priority gateway routing (higher timeout, better model)
- Batch scan (scan multiple pages into one PDF)

### Why This Model Works (from research data)

- Utility apps: avg $20-35/day per 1K DAU with ads (AdMob US eCPM $7.40)
- Scanner apps specifically: top-grossing Business category (TapScanner = #2 grossing in Brazil)
- Freemium with subscription: optimal for productivity tools (2-4% trial-to-paid conversion)
- Hybrid ads + subscription: highest total revenue (research shows 2-3x vs ads alone)

### Ad Placement Strategy

| View | Ad Format | Timing |
|---|---|---|
| Scan | Banner (bottom) | Always visible |
| Result | Banner (bottom) | Always visible |
| Summary | Banner (bottom) | Always visible |
| Translate | Banner (bottom) | Always visible |
| Settings | Banner (middle) | Embedded in list |
| Scan→Result transition | Interstitial | After every 3rd scan |

---

## 12. Play Store Deployment

### pyproject.toml

```toml
[project]
name = "doclens"
version = "1.0.0"
description = "AI Document Scanner — Smart Summary & Instant Translation"
requires-python = ">=3.13"
dependencies = [
    "flet==0.85.0",
    "flet-camera==0.85.0",
    "flet-ads==0.85.0",
    "flet-secure-storage==0.85.0",
    "httpx>=0.28.1",
]

[tool.flet]
org = "ng.kiri"
product = "DocLens"
build_number = 1

[tool.flet.app]
path = "src"

[tool.flet.android]
bundle_id = "ng.kiri.doclens"

[tool.flet.android.meta_data]
"com.google.android.gms.ads.APPLICATION_ID" = "<REAL_ADMOB_APP_ID>"

[tool.flet.android.permission]
"android.permission.INTERNET" = true
"android.permission.CAMERA" = true
"android.permission.READ_MEDIA_IMAGES" = true
"android.permission.ACCESS_NETWORK_STATE" = true

[tool.flet.ios.info]
NSCameraUsageDescription = "DocLens uses the camera to scan documents"
```

### Build & Sign

```bash
# Development
cd DocLens && uv run flet run

# Release APK
uv run flet build apk \
  --org ng.kiri \
  --bundle-id ng.kiri.doclens \
  --product "DocLens" \
  --build-version "1.0.0" \
  --build-number 1 \
  --android-signing-key-store "upload-keystore.jks" \
  --android-signing-key-alias "upload" \
  --android-signing-key-store-password "$STORE_PASS" \
  --android-signing-key-password "$KEY_PASS"

# Release AAB (for Play Store)
uv run flet build aab \
  --org ng.kiri \
  --bundle-id ng.kiri.doclens \
  --product "DocLens" \
  --build-version "1.0.0" \
  --build-number 1 \
  --android-signing-key-store "upload-keystore.jks" \
  --android-signing-key-alias "upload" \
  --android-signing-key-store-password "$STORE_PASS" \
  --android-signing-key-password "$KEY_PASS"
```

---

## 13. ASO Keywords

**App title**: DocLens — AI Document Scanner

**Short subtitle**: Smart Scan, Summary & Translate

**Long description keywords**: document scanner, PDF scanner, AI scanner, OCR scanner, text scanner, document AI, translate document, summarize PDF, scan to text, smart scanner, AI document reader

**Category**: Business (primary), Productivity (secondary)

**Why this works** (from MobileAction 2026 ASO report):
- "AI" is a top keyword across Productivity and Utilities
- "scan", "PDF", "document", "text" are the highest-volume Business category keywords
- "AI scanner" is an emerging long-tail with less competition than "PDF scanner"
- Utility apps with clear action keywords ("scan", "translate", "summarize") convert better

---

## 14. Development Phases

### Phase 1 — Core Scanner (3-4 days)

| # | Task | Files | Pattern Source |
|---|---|---|---|
| 1 | Scaffold project | `pyproject.toml`, `src/main.py` | KTV Player |
| 2 | State + theme + tokens + styles | `core/state.py`, `core/theme.py`, `core/tokens.py`, `core/styles.py` | FletBot |
| 3 | Constants (API URLs, secrets) | `core/constants.py` | Spaninsight |
| 4 | Camera service | `services/camera.py` | FletBot `services/camera.py` |
| 5 | File picker service | `services/file_picker.py` | FletBot `services/file_picker.py` |
| 6 | Credit service | `services/credit_service.py` | Spaninsight `services/credit_service.py` |
| 7 | Ad service | `services/ad_service.py` | KTV `services/ad_service.py` |
| 8 | Camera viewfinder component | `components/camera_viewfinder.py` | FletBot `components/camera_viewfinder.py` |
| 9 | Media preview component | `components/media_preview.py` | FletBot `components/media_preview.py` |
| 10 | Action button component | `components/action_button.py` | New |
| 11 | Ad banner component | `components/ad_banner.py` | KTV `ad_service.py` |
| 12 | Splash view | `views/splash.py` | KTV `views/splash.py` |
| 13 | Scan view | `views/scan.py` | FletBot `chat_view.py` |
| 14 | Result view | `views/result.py` | New |
| 15 | Settings view | `views/settings.py` | FletBot `views/settings_view.py` |
| 16 | Wire routing in main.py | `src/main.py` | Akili / Spaninsight |
| **Test** | Scan document → see in result → save PDF | — | — |

### Phase 2 — AI Features (3-4 days)

| # | Task | Files | Pattern Source |
|---|---|---|---|
| 1 | AI service (gateway client) | `services/ai_service.py` | FletBot + Spaninsight |
| 2 | Summary view (streaming markdown) | `views/summary.py` | FletBot `chat_view.py` |
| 3 | Translate view (language picker + result) | `views/translate.py` | New |
| 4 | Share service (copy + share) | `services/share.py` | FletBot `services/share.py` |
| 5 | Language data file | `assets/languages.json` | New |
| **Test** | Scan → AI summary → Translate to Spanish | — | — |

### Phase 3 — Polish & Release (2-3 days)

| # | Task | Details |
|---|---|---|
| 1 | Interstitial ads at transitions | After every 3rd scan |
| 2 | Premium flow (unlimited + no ads) | SecureStorage flag |
| 3 | OCR-text PDF export (premium) | Generate PDF with embedded text |
| 4 | Batch scan (premium) | Multiple pages → one PDF |
| 5 | Loading states + error handling | SnackBars, ProgressRings |
| 6 | Generate keystore, build AAB | `keytool` + `flet build aab` |
| 7 | Test on real Android device | `adb install` |
| 8 | Create Play Store listing | Screenshots, description, privacy policy |
| 9 | Upload AAB to Play Console | — |

---

## Appendix A: Flet Patterns Catalog

Every Flet pattern extracted from the 4 existing apps, referenced for quick lookup during development:

| Pattern | Source | File | Key API |
|---|---|---|---|
| `@ft.observable` state | All 4 apps | `core/state.py` | `@ft.observable class AppState` |
| Async routing | All 4 apps | `main.py` | `page.on_route_change = route_change` |
| View builders | All 4 apps | `views/*.py` | `def build_*_view(page, ...) -> ft.View` |
| Camera capture | FletBot | `services/camera.py` | `Camera().take_picture()` |
| Camera viewfinder | FletBot | `components/camera_viewfinder.py` | `ft.Stack` with `Camera` + controls |
| File picker | FletBot | `services/file_picker.py` | `ft.FilePicker().pick_files(with_data=True)` |
| Audio recorder | FletBot | `services/audio.py` | `AudioRecorder().start/stop_recording()` |
| AdMob banners | KTV Player | `services/ad_service.py` | `BannerAd(unit_id, width, height)` |
| AdMob interstitials | KTV Player | `services/ad_service.py` | `InterstitialAd(unit_id)` |
| Daily credits | Spaninsight | `services/credit_service.py` | `SecureStorage` + date check |
| Secure storage | FletBot | `auth/token_manager.py` | `flet_secure_storage.SecureStorage` |
| Markdown rendering | FletBot | `components/markdown_renderer.py` | `ft.Markdown(extension_set=GITHUB_WEB)` |
| Streaming AI | FletBot | `views/chat_view.py` | `async for chunk in runner.stream()` |
| Message bubbles | FletBot | `components/message_bubble.py` | `ft.Container` with gradient bg |
| Splash screen | KTV Player | `views/splash.py` | `ft.View` with centered column |
| Settings view | FletBot | `views/settings_view.py` | `section_header()` + `setting_tile()` |
| Design tokens | FletBot | `theme/tokens.py` | All spacing/radius/font constants |
| Glassmorphism | FletBot | `theme/colors.py` | `GLASS_BG`, `GLASS_BORDER_COLOR` |
| Theme toggle | FletBot | `views/settings_view.py` | `page.theme_mode` switch |
| Error handling | All 4 apps | `main.py` | `page.on_error`, `SnackBar` |
| Recording indicator | FletBot | `components/recording_indicator.py` | Timer + pulsing mic icon |
| Media preview bar | FletBot | `components/media_preview.py` | Chips with remove button |
| Quick action chips | FletBot | `components/quick_actions.py` | `ft.Button` with `chip_button_style()` |
