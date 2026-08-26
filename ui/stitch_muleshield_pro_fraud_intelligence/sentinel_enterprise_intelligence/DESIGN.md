---
name: Sentinel Enterprise Intelligence
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#45464d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#515f74'
  on-secondary: '#ffffff'
  secondary-container: '#d5e3fd'
  on-secondary-container: '#57657b'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#0b1c30'
  on-tertiary-container: '#75859d'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#d5e3fd'
  secondary-fixed-dim: '#b9c7e0'
  on-secondary-fixed: '#0d1c2f'
  on-secondary-fixed-variant: '#3a485c'
  tertiary-fixed: '#d3e4fe'
  tertiary-fixed-dim: '#b7c8e1'
  on-tertiary-fixed: '#0b1c30'
  on-tertiary-fixed-variant: '#38485d'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  title-sm:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 24px
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-caps:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '700'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-mono:
    fontFamily: JetBrains Mono
    fontSize: 12px
    fontWeight: '450'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  unit: 4px
  container-margin: 24px
  gutter: 16px
  table-row-height: 40px
  sidebar-width: 260px
---

## Brand & Style
The design system is engineered for high-stakes financial surveillance and forensic analysis. It prioritizes **Institutional Trust** and **Cognitive Efficiency**, ensuring that investigators can process high-density data without fatigue. 

The aesthetic is **Corporate / Modern** with a focus on systematic clarity. It avoids decorative flourishes in favor of functional precision. The interface must feel authoritative and stable, utilizing a "Glass and Steel" philosophy: rigid structural integrity paired with clear, layered information panels. The emotional response is one of calm control amidst complex data landscapes.

## Colors
The palette is anchored by **Deep Navy (#0f172a)**, used exclusively for primary navigation and high-level structural headers to establish authority. The main workspace utilizes **Slate Gray (#f8fafc)** to reduce glare during long shifts.

Accent colors are strictly functional:
- **Success Green:** Used for verified entities and cleared alerts.
- **Warning Amber:** Used for suspicious patterns requiring review.
- **Critical Red:** Reserved for confirmed fraud and immediate threats.
- **Info Blue:** Used for neutral system notifications and links.

Neutral scales are highly granular to differentiate between background layers, borders, and inactive text states.

## Typography
This design system uses **Inter** for all UI elements to ensure maximum legibility across varied display qualities. For technical strings—such as Transaction IDs, SWIFT codes, and IP addresses—**JetBrains Mono** is employed to prevent character confusion (e.g., 0 vs O).

**Hierarchy Rules:**
- **Display & Headlines:** Use tight letter-spacing for a modern, "locked-in" professional look.
- **Data Tables:** Use `body-sm` for primary rows to maximize information density.
- **Labels:** Use `label-caps` for table headers and section overlines to differentiate from interactive data.

## Layout & Spacing
The system follows a **Fixed-Fluid Hybrid** model. The primary sidebar is fixed at 260px, while the main workspace expands to fill the viewport. Content is organized within a 12-column grid system.

**Spacing Philosophy:**
- Use a strictly 4px base unit. 
- **Density:** Elements are packed tightly (8px–12px padding) within data-heavy views (Worklists) and more generously (24px+) in analytical views (Case Details).
- **Responsive Behavior:** On tablet displays, the sidebar collapses into an icon-only rail to preserve horizontal space for data tables. Mobile views are limited to read-only status dashboards and urgent approval flows.

## Elevation & Depth
Depth is conveyed through **Tonal Layering** rather than heavy shadows to maintain a clean, professional profile.

- **Level 0 (Background):** #f8fafc (Slate-50) – The canvas.
- **Level 1 (Cards/Panels):** #ffffff (White) with a 1px border (#e2e8f0). Used for primary content blocks.
- **Level 2 (Modals/Popovers):** #ffffff with a subtle, diffuse shadow (0 4px 12px rgba(15, 23, 42, 0.08)).
- **Interactive States:** Subtle 1px inset shadows on active buttons or focused input fields to simulate a physical "press."

## Shapes
The shape language is **Soft (0.25rem)**. This provides a subtle modern touch without sacrificing the serious, institutional feel of the platform.

- **Small Components:** Checkboxes, tags, and small buttons use the 0.25rem radius.
- **Large Components:** Workspace cards and modals use `rounded-lg` (0.5rem) to distinguish them from the base layout.
- **Status Indicators:** Status pips are perfectly circular, but status "pills" (tags) use the standard 0.25rem radius for a more architectural look.

## Components
**Data Tables:** 
The core of the experience. Tables must feature sticky headers, alternating row stripes (Slate-50/White), and a "High-Contrast" mode for accessibility. Row height is capped at 40px for maximum density.

**Status Chips:**
Small, rectangular tags with a subtle background tint and a high-contrast dot indicator. For example: A "High Risk" chip has a light red background, dark red text, and a solid red circular pip.

**Buttons:**
- **Primary:** Solid Deep Navy (#0f172a) with white text.
- **Secondary:** White background with a Slate-300 border.
- **Ghost:** No background/border; text changes to Primary color on hover.

**Input Fields:**
Large, clear labels positioned above the field. Border-color changes to Info Blue (#3b82f6) on focus with a 2px outer "halo" of the same color at 10% opacity.

**Audit Timeline:**
A vertical layout component using a thin center-line and icons to denote case transitions, comments, and automated system flags.