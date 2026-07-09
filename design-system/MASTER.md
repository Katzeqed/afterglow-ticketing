# Afterglow — Design System

**Style:** Warm Analog Editorial — a single-artist tour site (MARLOWE — *Afterglow*).
Warm paper base, one earthy accent, oversized editorial serif, film grain, restrained motion.

Tokens live in `frontend/src/index.css` (`@theme`) and are consumed as Tailwind
utilities (`bg-paper`, `text-ink`, `text-terracotta`, `font-display`, …).

## Color

| Role | Token | Hex |
|------|-------|-----|
| Background (paper) | `--color-paper` | `#F4EFE6` |
| Surface | `--color-surface` | `#EAE3D6` |
| Text (ink) | `--color-ink` | `#211E1A` |
| Muted text | `--color-muted` | `#6B635A` |
| Hairline | `--color-line` | `#D9D0C2` |
| Accent (CTA, selection) | `--color-terracotta` | `#C0603B` |
| Accent hover | `--color-terracotta-dark` | `#A34E2E` |
| Zone · Floor | `--color-sage` | `#7A8B6F` |
| Zone · Balcony | `--color-amber` | `#D69A4C` |

Single accent rule: terracotta only for calls-to-action and the selected state.
Zone colors are data-driven (served by the API per zone).

### Seat status colors (map)
Status is never conveyed by color alone — shape/opacity/stroke also change.

| Status | Fill | Extra |
|--------|------|-------|
| available | zone color, 0.9 opacity | pointer cursor |
| selected | zone color, full opacity | ink stroke, larger radius |
| held (others) | `#D69A4C`, 0.4 opacity | not selectable |
| booked | `#C9C0B2`, 0.55 opacity | not selectable |

## Typography

| Role | Font | Usage |
|------|------|-------|
| Display | **Playfair Display** (`--font-display`) | artist name, headings, prices |
| Body / UI | **Inter** (`--font-body`) | everything else |

- Hero uses `clamp(3.5rem, 15vw, 11rem)`, weight 700, tight tracking.
- Uppercase labels use `tracking-[0.2em]–[0.35em]`, 11–12px, muted.

## Motion (Framer Motion)

- Animate 1–2 elements per view — never everything.
- Entrances: fade + 16px rise, `easeOut`, ~0.5s (`components/Reveal`).
- Tour dates: stagger children ~0.06s.
- Seat selection: cheap CSS transition on the SVG circle (not a JS lib — 500 nodes).
- Confirmation check: spring scale-in.
- `MotionConfig reducedMotion="user"` — respects `prefers-reduced-motion`.

## Texture

- Film grain: fixed full-screen SVG `feTurbulence` overlay, opacity `0.05`,
  `mix-blend-multiply`, `pointer-events-none` (`components/GrainOverlay`).

## Layout

- Content max-width: `max-w-3xl`–`max-w-5xl`, centered, generous vertical rhythm.
- Sharp corners (no border-radius) except pills/dots — editorial feel.
- Hairline `border-line` dividers instead of shadows.
- Sticky selection bar on the seat map; two-column checkout collapses on mobile.

## Accessibility

- Contrast ≥ 4.5:1 (dark ink on warm paper).
- Seat status not color-only (opacity/stroke differ).
- `prefers-reduced-motion` honored globally.
- Responsive at 375 / 768 / 1024 / 1440.
