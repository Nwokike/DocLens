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
- [11. Monetization (Daily Credits + Rewarded Ads)](#11-monetization-daily-credits--rewarded-ads)
- [12. Image Preprocessing Pipeline](#12-image-preprocessing-pipeline)
- [13. Play Store Deployment](#13-play-store-deployment)
- [14. ASO Keywords](#14-aso-keywords)
- [15. Development Phases](#15-development-phases)
- [Appendix A: Flet Patterns Catalog](#appendix-a-flet-patterns-catalog)

---

## 1. Product Overview

### What It Does

DocLens is a single-app trifecta:

| Feature | Trigger | AI Route | Output |
|---|---|---|---|
| **Smart Scanner** | Camera or gallery | `multimodal` | Clean, straightened, enhanced document image |
| **AI Summary** | One tap after scan | `multimodal` → `text` | Bullet-point tl;dr of document contents |
| **Smart Translate** | One tap after scan | `text` (uses cached OCR) | Document text in user's chosen language |

All three share the same camera/gallery entry point — no separate flows.

### Why This Wins

- **Shared funnel**: One camera flow feeds all 3 features — minimal code, maximum value.
- **Daily use**: People scan documents every day = ad impressions compound.
- **AI is the unlock**: Most scanner apps have OCR. Almost none have AI summary + translate in one tap. Adobe Scan just added "Generative summary" in 2025 and it propelled them to #5 grossing in the Business category.
- **Proven market**: CamScanner ($5.6M/mo), Adobe Scan (#5 grossing Business), TapScanner (#2 grossing in Brazil), iScanner (125M+ users). The scanner category is validated.

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
Image captured (raw 12MP+)
        │
        ▼
Preprocessing Pipe (core/utils.py)
   ├── Resize to max 1600px (Pillow thumbnail)
   ├── JPEG quality 80
   └── Returns optimized bytes (~200-500KB)
        │
        ▼
Preview in Scan Result view
        │
        ├── "AI Summary"
        │     ├── POST /chat {task_type: "multimodal", image: base64}
        │     │   → extracts all text from document
        │     │   → CACHE extracted text in AppState
        │     ├── POST /chat {task_type: "text", "Summarize this..."}
        │     │   → bullet-point summary (streaming markdown)
        │     └── REWARDED AD (unlock summary if daily credits exhausted)
        │
        ├── "Translate"
        │     ├── Uses CACHED text from AppState
        │     │   (no second multimodal call — text-to-text only)
        │     ├── POST /chat {task_type: "text", "Translate to X..."}
        │     │   → translated text (streaming markdown)
        │     └── REWARDED AD (unlock translate if daily credits exhausted)
        │
        └── "Save PDF"
              └── fpdf2 → PDF with embedded image → Save to Downloads
```

### Key Design Decisions

- **No local database** — scan history is ephemeral in-session. Users save PDFs to device storage. Avoids Play Store data-deletion policy complexity.
- **Local-only credits** — daily scan limit stored in `flet-secure-storage` (pattern from Spaninsight). No backend needed.
- **AI calls go through `kiri-gateway`** — every app uses the same gateway. Gateway handles fallback chains, multi-key rotation, auth.
- **Camera and gallery share same callback** — same `on_image_captured(data, mime, filename)` handler regardless of source.
- **OCR result cached in AppState** — Summary and Translate both need the extracted text. First call stores it; subsequent calls reuse it. Translate is always text-to-text only — no second multimodal call.
- **Rewarded ads unlock AI features** — when daily credits are used up, users watch a 30s video to "Unlock AI Analysis." This triples eCPM vs banners.

---

## 3. Routes & Navigation

```
/splash     → Logo + loading bar (1.5s then go)
/scan       → Main camera/gallery entry
/result     → Shows captured image + action buttons (Summary, Translate, Save PDF)
/summary    → Stage-signaled AI summary with streaming markdown
/translate  → Language picker → streaming translation
/settings   → Theme toggle, credit info, about, ad banner
```

### Route Change Handler

```python
async def route_change(e=None):
    page.views.clear()
    if page.route == "/splash":
        page.views.append(build_splash_view(page, navigate))
    elif page.route == "/scan":
        page.views.append(build_scan_view(page, navigate, on_captured))
    elif page.route == "/result":
        page.views.append(build_result_view(page, navigate, state))
    elif page.route == "/summary":
        page.views.append(build_summary_view(page, navigate, state))
    elif page.route == "/translate":
        page.views.append(build_translate_view(page, navigate, state))
    elif page.route == "/settings":
        page.views.append(build_settings_view(page, navigate))
    page.update()

page.on_route_change = route_change
page.on_view_pop = view_pop
```

---

## 4. Project Structure

```
DocLens/
├── pyproject.toml
├── src/
│   ├── main.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── state.py          # @ft.observable AppState singleton
│   │   ├── theme.py          # Color palette
│   │   ├── tokens.py         # Spacing, radius, font sizes
│   │   ├── styles.py         # Reusable widget factories
│   │   ├── constants.py      # API URL, secrets, ad IDs
│   │   └── utils.py          # Image preprocessing (resize, compress)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ai_service.py     # kiri-gateway client
│   │   ├── camera.py         # flet-camera wrapper (FletBot pattern)
│   │   ├── file_picker.py    # ft.FilePicker wrapper (FletBot pattern)
│   │   ├── ad_service.py     # flet-ads wrapper (KTV pattern)
│   │   ├── credit_service.py # Daily scan credits (Spaninsight pattern)
│   │   └── share.py          # Clipboard + share + PDF save
│   ├── views/
│   │   ├── __init__.py
│   │   ├── splash.py         # Splash screen
│   │   ├── scan.py           # Camera / gallery entry
│   │   ├── result.py         # Scan preview + action buttons
│   │   ├── summary.py        # AI summary with stage signaling
│   │   ├── translate.py      # Language picker + translation
│   │   └── settings.py       # Preferences, credits, about
│   └── components/
│       ├── __init__.py
│       ├── camera_viewfinder.py  # Full-screen camera overlay
│       ├── media_preview.py      # Staged image preview
│       ├── action_button.py      # Feature button (Summary/Translate/Save)
│       ├── ad_banner.py          # Inline banner ad wrapper
│       └── status_overlay.py     # Stage signaling overlay for AI processing
└── assets/
    ├── icon.png
    └── languages.json
```

---

## 5. Theme & Design System

### Colors (`core/theme.py`) — "Clean White / Cyber Blue"

```python
PRIMARY = "#2563EB"          # Cyber blue (trustworthy, tech-forward)
PRIMARY_DARK = "#1D4ED8"
ACCENT = "#06B6D4"           # Cyan accent
SURFACE_LIGHT = "#FFFFFF"
SURFACE_DARK = "#0F172A"
TEXT_PRIMARY = "#1E293B"
TEXT_SECONDARY = "#64748B"
SUCCESS = "#10B981"
WARNING = "#F59E0B"
ERROR = "#EF4444"
```

### Tokens (`core/tokens.py`)

Same pattern as `fletbot/src/theme/tokens.py` — `RADIUS_*`, `SPACE_*`, `FONT_*`, `ICON_*`, `ANIMATION_MS`, `BLUR_*`. Every magic number in one file.

### Styles (`core/styles.py`)

- `glass_card(content, width, padding)` — frosted-glass container
- `standard_appbar(title, leading, actions)` — consistent AppBar
- `section_header(title)` — settings section label
- `setting_tile(icon, title, subtitle, trailing)` — settings row
- `primary_button(text, on_click)` — filled primary CTA
- `action_chip(icon, label, color, on_click)` — result view action
- `status_banner(text, icon, color)` — stage signaling banner

### Icons

Use built-in `ft.Icons` (Lucide/Material icons). No designer needed. The Cyber Blue + White theme looks premium for free.

---

## 6. State Management

Pattern from Spaninsight/Akili/KTV — `@ft.observable` singleton:

```python
@ft.observable
class AppState:
    # Image
    current_image: bytes | None = None
    current_image_mime: str = ""
    current_image_name: str = ""

    # Cached OCR result (prevents duplicate multimodal calls)
    extracted_text: str = ""

    # AI Results
    current_summary: str = ""
    current_translation: str = ""
    current_target_language: str = "es"

    # Stage signaling
    processing_stage: str = ""       # "Optimizing image..." → "Reading text..."
    is_processing: bool = False

    # Credits (local-only, SecureStorage)
    scans_today: int = 0
    daily_scan_limit: int = 5

    # Theme
    theme_mode: ft.ThemeMode = ft.ThemeMode.LIGHT

    def clear_scan(self):
        self.current_image = None
        self.current_image_mime = ""
        self.current_image_name = ""
        self.extracted_text = ""
        self.current_summary = ""
        self.current_translation = ""

state = AppState()
```

---

## 7. Service Layer

### ai_service.py — Pattern from FletBot + Spaninsight

```python
async def analyze_document(image_bytes, mime_type, on_stage=None) -> str
    # Stage 1: on_stage("Optimizing image...")
    # Stage 2: on_stage("Uploading to DocLens AI...")
    # Stage 3: on_stage("Reading text...")
    # Returns extracted text, CACHED in AppState

async def summarize(text, stream_callback, on_stage=None) -> str
    # Stage: on_stage("Generating summary...")
    # Streaming markdown response

async def translate(text, target_lang, stream_callback, on_stage=None) -> str
    # Stage: on_stage("Translating...")
    # text-to-text only (uses cached extracted_text)
```

Uses `httpx.AsyncClient` with 30s timeout. Auth: `Authorization: Bearer <GATEWAY_SECRET>`.

### camera.py — Pattern from FletBot

```python
class CameraService:
    async def capture_photo() -> tuple[bytes, str] | None
        # Camera().take_picture() → raw bytes → resize → return
```

Same structure as `fletbot/src/services/camera.py`. Uses `flet_camera.Camera`, `ResolutionPreset.MEDIUM`.

### file_picker.py — Pattern from FletBot + Akili

```python
class FilePickerService:
    def pick_image(on_result)
        # ft.FilePicker.pick_files(allowed_extensions=["jpg","jpeg","png","webp"], with_data=True)
```

### ad_service.py — Pattern from KTV Player (production)

- Preload interstitial on startup
- Banner ads embedded in views
- Rewarded video ads for "Unlock AI" when credits exhausted
- Re-preload after close
- Platform check: `page.platform.is_mobile()`

```python
class AdService:
    async def preload_interstitial()
    async def show_interstitial() -> bool
    async def show_rewarded_ad() -> bool   # NEW: for unlocking AI features
    def get_banner_ad() -> ft.Control
```

### credit_service.py — Pattern from Spaninsight

```python
class CreditService:
    async def initialize() -> int
    async def can_scan() -> bool
    async def use_scan() -> bool
    async def get_remaining() -> int
```

All local via `flet-secure-storage`. Daily reset. 5 free scans/day. Rewarded ads can grant 1 extra scan.

### share.py — Pattern from FletBot

```python
class ShareService:
    async def copy_text(text)
    async def share_text(text)
    async def save_as_pdf(image_bytes, title)  # Uses fpdf2
    async def save_as_document(text, title)     # Saves markdown/text as doc
```

### core/utils.py — Image Preprocessing (NEW)

```python
from PIL import Image
import io

def prepare_image_for_ai(image_bytes: bytes) -> bytes:
    """Resize to max 1600px, JPEG quality 80. Reduces 10MB → ~300KB."""
    img = Image.open(io.BytesIO(image_bytes))
    img.thumbnail((1600, 1600))  # Maintains aspect ratio
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=80)
    return buffer.getvalue()
```

Applied after camera capture AND file picker, before any base64 encoding. Prevents OOM crashes, reduces upload time on 4G.

---

## 8. Views (Detailed)

### splash.py (`/splash`)

- Logo + "DocLens" + "AI Document Scanner"
- Progress bar (1.5s)
- Check credit daily reset
- Navigate to `/scan`
- Pattern: `ktv-player/src/views/splash.py`

### scan.py (`/scan`)

- Two large buttons:
  - **Take Photo** → `CameraViewfinder` overlay
  - **Choose from Gallery** → `FilePicker`
- Bottom banner ad
- Header with credit counter + settings gear
- Pattern: FletBot's `_on_camera` + `_on_attach`

### result.py (`/result`)

- Captured image in rounded container
- Three action buttons row:
  - **AI Summary** (sparkles icon)
  - **Translate** (language icon)
  - **Save PDF** (download icon)
- Credit counter top-right
- Bottom banner ad
- Stage signaling: if credits exhausted, show "Watch ad to unlock" with rewarded ad

### summary.py (`/summary`)

- AppBar: "AI Summary" with back
- Calls `analyze_document` with stage signaling:
  - "Optimizing image..."
  - "Uploading to DocLens AI..."
  - "Reading text..."
  - "Generating summary..."
- Streaming markdown response (pattern: FletBot's `MarkdownRenderer`)
- Copy button + Share button + **Save as Document** button
- Banner ad at bottom
- If daily credits used: show Rewarded Ad first

### translate.py (`/translate`)

- Step 1: Language picker (`ft.Dropdown` with common languages)
  - English, Spanish, French, German, Chinese, Japanese, Arabic, Portuguese
- Step 2: Uses `state.extracted_text` (cached from summary) — no second multimodal call
- Stage signaling: "Translating..."
- Shows original + translated text side by side
- Both selectable and copyable
- Swap languages button
- Save as Document button

### settings.py (`/settings`)

- Pattern: `fletbot/src/views/settings_view.py`
- Section: **SCANNING**
  - Today's scans (x/5 with progress bar)
- Section: **APPEARANCE**
  - Theme toggle (Light/Dark)
- Section: **ABOUT**
  - Version
  - Kiri Gateway
  - Privacy policy
- Section: **DATA SAFETY**
  - "Images are sent to our AI gateway for processing. Data encrypted in transit. Not shared with third parties."
- Banner ad in middle

---

## 9. Components (Detailed)

### CameraViewfinder

Full-screen overlay. Pattern from `fletbot/src/components/camera_viewfinder.py`.

- `ft.Stack` with camera preview + capture button + close + flip
- Capture: white circle with blue border, scale animation
- On capture: `on_capture(bytes, mime, filename)` → close

### MediaPreview

Shows selected image before navigating to result. Pattern from `fletbot/src/components/media_preview.py`.

### ActionButton

```python
ActionButton(icon=ft.Icons.AUTO_AWESOME, label="AI Summary", color=PRIMARY, on_click)
```

- Container with icon + label + color tint background
- Ripple on tap, scale animation

### AdBanner

Inline banner ad. Pattern from `ktv-player/src/services/ad_service.py`.

- `BannerAd` in centered container
- No-op on desktop/web

### StatusOverlay (NEW)

Stage signaling overlay for AI processing:

```
┌──────────────────────────────┐
│  🔄 Optimizing image...      │
│  [━━━━━━━━━━━━━━━━] 80%      │
│                              │
│  "AI is reading your         │
│   document. This may take    │
│   a few seconds."            │
└──────────────────────────────┘
```

- Shows current stage text
- Animated progress indicator
- Updates as AI service reports stages
- Pattern: combines elements from FletBot's `ThinkingIndicator` + `RecordingIndicator`

---

## 10. Gateway Integration

DocLens → `https://api.kiri.ng/chat`

### Auth

```
Authorization: Bearer <GATEWAY_SECRET>
Content-Type: application/json
```

### Task Types

| Task Type | When | Notes |
|---|---|---|
| `multimodal` | First AI call (analyze document) | Image as base64 data URI. Stream=false. |
| `text` | Summary | Uses extracted text. Stream=true. |
| `text` | Translate | Uses cached extracted text. Stream=true. |

### Critical: Cache OCR Result

```python
# In summary view:
if not state.extracted_text:
    # First time — call multimodal
    state.extracted_text = await ai_service.analyze_document(...)

# In translate view:
# Uses state.extracted_text directly — no second multimodal call
text_to_translate = state.extracted_text
```

This prevents duplicate multimodal calls when user taps both Summary and Translate.

### constants.py

```python
API_BASE_URL = "https://api.kiri.ng"
API_CHAT_ENDPOINT = f"{API_BASE_URL}/chat"
GATEWAY_SECRET = "doclens-mobile-v1"
USER_AGENT = "DocLens/1.0.0"
```

---

## 11. Monetization (Daily Credits + Rewarded Ads)

### Free Tier (Daily Credits)

| Resource | Limit |
|---|---|
| Document scans | 5 per day (resets daily via SecureStorage) |
| AI Summary | Included in scan credit |
| Translation | Included in scan credit |
| Banner ads | Always visible at bottom |
| Save as PDF | Always available |
| Save as Document | Always available |

### Rewarded Ads (Extra Scans)

When daily credits exhausted, user can:
- **Watch a 30s Rewarded Video** → get 1 extra scan
- This replaces the subscription model entirely
- Rewarded ads earn $10–$30+ eCPM (vs $5–$15 for interstitials, $0.50–$2 for banners)

### Ad Revenue Strategy (from 2026 data)

- **Primary**: Rewarded video (unlock AI features) — highest eCPM
- **Secondary**: Interstitial at scan transitions
- **Passive**: Banner at bottom of every view
- Typical utility app: $20–35/day per 1K DAU
- With rewarded ads added: potentially 2-3x that

---

## 12. Image Preprocessing Pipeline

### core/utils.py

```python
from PIL import Image
import io

MAX_WIDTH = 1600
JPEG_QUALITY = 80

def prepare_image_for_ai(image_bytes: bytes) -> bytes:
    """Downscale and compress image for AI processing.
    
    Modern phones shoot 12MP+ (5-10MB). Sending raw base64 will:
    - Crash the app (OOM)
    - Take forever on 4G
    - AI models don't need 4K to read text
    
    This reduces to ~200-500KB with no meaningful quality loss for OCR.
    """
    img = Image.open(io.BytesIO(image_bytes))
    
    # Convert to RGB if RGBA (JPEG doesn't support alpha)
    if img.mode == "RGBA":
        img = img.convert("RGB")
    
    # Resize while maintaining aspect ratio
    img.thumbnail((MAX_WIDTH, MAX_WIDTH))
    
    # Compress
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=JPEG_QUALITY)
    
    return buffer.getvalue()
```

---

## 13. Play Store Deployment

### pyproject.toml

```toml
[project]
name = "doclens"
version = "1.0.0"
description = "AI Document Scanner — Smart Summary & Instant Translate"
requires-python = ">=3.13"
dependencies = [
    "flet==0.85.0",
    "flet-camera==0.85.0",
    "flet-ads==0.85.0",
    "flet-secure-storage==0.85.0",
    "httpx>=0.28.1",
    "Pillow>=11.0.0",
    "fpdf2>=2.8.0",
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
# NO: MANAGE_EXTERNAL_STORAGE — Google will reject

[tool.flet.ios.info]
NSCameraUsageDescription = "DocLens uses the camera to scan documents"
```

### Play Store Guardrails

| Requirement | How DocLens Handles It |
|---|---|
| **Permissions** | Only CAMERA + READ_MEDIA_IMAGES. No MANAGE_EXTERNAL_STORAGE. |
| **Data Safety** | Data Safety form discloses: data encrypted in transit, sent to server for AI processing, not shared with third parties. |
| **File Saving** | PDFs saved to app's scoped storage via `fpdf2`. User can share/save from there. No "All Files Access" needed. |
| **Privacy Policy** | Hosted page stating: images are sent to our AI processing gateway, data encrypted in transit, not stored permanently, not shared. |

### Build

```bash
# Scaffold
mkdir doclens && cd doclens
uv run flet create

# Dev
uv run flet run

# Release AAB
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

## 14. ASO Keywords

**App title**: DocLens — AI Document Scanner

**Short subtitle**: Smart Scan, Summary & Translate

**Keywords**: document scanner, AI scanner, PDF scanner, OCR scanner, note summarizer, study helper AI, invoice scanner, scan to text, translate document, AI document reader, homework scanner, text extractor

**Category**: Business (primary), Productivity (secondary)

**Screenshots (first two)**:
1. Before/after: messy handwritten note → clean bulleted list (shows AI Summary)
2. Before/after: foreign language menu → English translation (shows Translate)

---

## 15. Development Phases

### Phase 1 — Core Scanner (3-4 days)

| # | Task | Pattern Source |
|---|---|---|
| 1 | `uv run flet create` — scaffold project | Flet CLI |
| 2 | `core/state.py` + `core/theme.py` + `core/tokens.py` + `core/styles.py` | FletBot |
| 3 | `core/constants.py` (API URLs) | Spaninsight |
| 4 | `core/utils.py` (image preprocessing with Pillow) | New |
| 5 | `services/camera.py` | FletBot |
| 6 | `services/file_picker.py` | FletBot |
| 7 | `services/credit_service.py` | Spaninsight |
| 8 | `services/ad_service.py` (with rewarded ad support) | KTV Player |
| 9 | `components/camera_viewfinder.py` | FletBot |
| 10 | `components/media_preview.py` | FletBot |
| 11 | `components/action_button.py` + `components/ad_banner.py` | New + KTV |
| 12 | `views/splash.py` | KTV Player |
| 13 | `views/scan.py` | FletBot |
| 14 | `views/result.py` | New |
| 15 | `views/settings.py` | FletBot |
| 16 | Wire routing in `main.py` | Akili / Spaninsight |
| **Test** | Scan → Result → Save PDF | Real device |

### Phase 2 — AI Features (3-4 days)

| # | Task | Pattern Source |
|---|---|---|
| 1 | `services/ai_service.py` (with stage callbacks) | FletBot + Spaninsight |
| 2 | `components/status_overlay.py` (stage signaling) | New |
| 3 | `views/summary.py` (stage signaling + streaming markdown) | FletBot chat_view |
| 4 | `views/translate.py` (language picker + cached OCR) | New |
| 5 | `services/share.py` (clipboard + fpdf2 PDF + doc save) | FletBot |
| 6 | `assets/languages.json` | New |
| **Test** | Scan → AI Summary → Translate → Save as Document | Real device |

### Phase 3 — Polish & Release (2-3 days)

| # | Task |
|---|---|
| 1 | Rewarded ad flow for extra scans |
| 2 | Stage signaling polish (timing, animations) |
| 3 | Loading/error/empty states everywhere |
| 4 | Generate keystore, build AAB |
| 5 | Test on real Android device |
| 6 | Play Store listing + screenshots + privacy policy |
| 7 | Upload AAB to Play Console |

---

## Appendix A: Flet Patterns Catalog

| Pattern | Source | Key API |
|---|---|---|
| `@ft.observable` state | All 4 apps | `@ft.observable class AppState` |
| Async routing | All 4 apps | `page.on_route_change = route_change` |
| View builders | All 4 apps | `def build_*_view(page, ...) -> ft.View` |
| Camera capture | FletBot | `Camera().take_picture()` |
| Camera viewfinder | FletBot | `ft.Stack` with `Camera` + controls |
| File picker | FletBot | `ft.FilePicker().pick_files(with_data=True)` |
| Audio recorder | FletBot | `AudioRecorder().start/stop_recording()` |
| AdMob banners | KTV Player | `BannerAd(unit_id, width, height)` |
| AdMob interstitials | KTV Player | `InterstitialAd(unit_id)` |
| Rewarded ads | (2026 standard) | `RewardedAd(unit_id)` |
| Daily credits | Spaninsight | `SecureStorage` + date check |
| Secure storage | FletBot | `flet_secure_storage.SecureStorage` |
| Markdown rendering | FletBot | `ft.Markdown(extension_set=GITHUB_WEB)` |
| Streaming AI | FletBot | `async for chunk in response` |
| Splash screen | KTV Player | Centered column with progress |
| Settings view | FletBot | `section_header()` + `setting_tile()` |
| Design tokens | FletBot | All spacing/radius/font constants |
| Glassmorphism | FletBot | `GLASS_BG`, `GLASS_BORDER_COLOR` |
| Theme toggle | FletBot | `page.theme_mode` switch |
| Error handling | All 4 apps | `SnackBar`, `page.on_error` |
| Recording indicator | FletBot | Timer + pulsing animation |
| Media preview | FletBot | Chips with remove button |
| Quick actions | FletBot | `ft.Button` with chip style |
