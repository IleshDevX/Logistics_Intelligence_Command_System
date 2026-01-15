# LICS UI Style Guide - Quick Reference

## 🎨 Color Palette

### Primary Colors
```css
/* Backgrounds */
--bg-primary: #FAFAFA      /* Page background */
--bg-secondary: #F5F7F9    /* Sidebar background */
--bg-card: #FFFFFF         /* Card/panel background */
--bg-tile: #F9FAFB         /* Info tile background */

/* Text */
--text-primary: #2E2E2E    /* Headlines, main text */
--text-secondary: #6B7280  /* Labels, captions */

/* Borders & Lines */
--border-color: #E5E7EB    /* Card borders, dividers */
--shadow: 0 1px 3px rgba(0,0,0,0.08)  /* Card shadows */
```

### Risk Colors (Soft Tones)
```css
/* LOW Risk */
--risk-low-bg: #D1FAE5     /* Soft green background */
--risk-low-text: #065F46   /* Dark green text */

/* MEDIUM Risk */
--risk-medium-bg: #FEF3C7  /* Soft amber background */
--risk-medium-text: #92400E /* Dark amber text */

/* HIGH Risk */
--risk-high-bg: #FEE2E2    /* Soft red background */
--risk-high-text: #991B1B  /* Dark red text */
```

### Accent Colors
```css
--accent-blue: #60A5FA     /* Primary actions, links */
--accent-amber: #F59E0B    /* Warnings, cautions */
--accent-green: #10B981    /* Success states */
```

---

## 📐 Spacing System

```css
--spacing-xs: 0.25rem   /* 4px */
--spacing-sm: 0.5rem    /* 8px */
--spacing-md: 1rem      /* 16px */
--spacing-lg: 1.5rem    /* 24px */
--spacing-xl: 2rem      /* 32px */
```

---

## 📝 Typography

### Font Sizes
```css
--font-xs: 0.75rem      /* 12px - Small labels */
--font-sm: 0.875rem     /* 14px - Body text */
--font-base: 0.9rem     /* 14.4px - Default */
--font-lg: 1.1rem       /* 17.6px - Headers */
--font-xl: 1.5rem       /* 24px - Metric values */
--font-2xl: 2rem        /* 32px - Large metrics */
```

### Font Weights
```css
--font-normal: 400      /* Regular text */
--font-medium: 500      /* Emphasis */
--font-semibold: 600    /* Headers */
--font-bold: 700        /* Metrics */
```

---

## 🧩 Component Library

### Card Component
```html
<div style="
    background: #FFFFFF;
    padding: 1.5rem;
    border-radius: 8px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    margin-bottom: 1rem;
">
    Content here
</div>
```

### Risk Badge Component
```html
<!-- LOW Risk -->
<span style="
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 4px;
    font-weight: 600;
    font-size: 0.9rem;
    background: #D1FAE5;
    color: #065F46;
">
    🟢 Low Risk
</span>

<!-- MEDIUM Risk -->
<span style="
    background: #FEF3C7;
    color: #92400E;
    /* ... rest same as above */
">
    🟡 Medium Risk
</span>

<!-- HIGH Risk -->
<span style="
    background: #FEE2E2;
    color: #991B1B;
    /* ... rest same as above */
">
    🔴 High Risk
</span>
```

### Info Tile Component
```html
<div style="
    background: #F9FAFB;
    padding: 1rem;
    border-radius: 6px;
    border-left: 3px solid #60A5FA;
    margin-bottom: 0.5rem;
">
    <div style="
        font-size: 0.75rem;
        color: #6B7280;
    ">Label</div>
    <div style="
        font-weight: 600;
        color: #2E2E2E;
    ">Value</div>
</div>
```

### Metric Card Component
```html
<div style="
    background: #FFFFFF;
    padding: 1.25rem;
    border-radius: 8px;
    border: 1px solid #E5E7EB;
    text-align: center;
">
    <div style="
        font-size: 2rem;
        font-weight: 700;
        color: #2E2E2E;
    ">42</div>
    <div style="
        font-size: 0.875rem;
        color: #6B7280;
        margin-top: 0.25rem;
    ">Metric Label</div>
</div>
```

### Section Header
```html
<div style="
    color: #2E2E2E;
    font-size: 1.1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #E5E7EB;
">
    Section Title
</div>
```

---

## 🎯 Usage Guidelines

### When to Use Risk Colors

✅ **DO USE:**
- Risk band badges
- Risk level indicators
- Metric highlighting (when thresholds exceeded)

❌ **DON'T USE:**
- Large background areas
- Body text
- Navigation elements
- Decorative elements

### Whitespace Rules

**Always include:**
- 1rem margin between sections
- 1.5rem padding inside cards
- 0.5rem gap between form elements
- 2rem padding at top/bottom of main content

### Text Hierarchy

1. **Primary**: Page titles, key decisions
2. **Secondary**: Section headers, labels
3. **Tertiary**: Captions, hints, timestamps

---

## 📊 Chart Styling

```python
# Streamlit bar chart
st.bar_chart(data, color="#60A5FA")  # Blue for primary
st.bar_chart(data, color="#F59E0B")  # Amber for warnings

# Height: 300-400px max
# Background: Transparent or white
# Grid: Minimal or none
```

---

## 🚦 State Indicators

### Success State
```python
st.success("✅ Operation completed successfully")
# Color: Soft green
# Icon: ✅
```

### Warning State
```python
st.warning("⚠️ Review required")
# Color: Soft amber
# Icon: ⚠️
```

### Error State
```python
st.error("❌ Validation failed")
# Color: Soft red
# Icon: ❌
```

### Info State
```python
st.info("💡 Helpful information")
# Color: Soft blue
# Icon: 💡
```

---

## 🔤 Icon Library

```
📦 Shipment/Parcel
🧑‍💼 Manager
📊 Supervisor/Analytics
📍 Location/Route
🏙️ Area/City
⏱️ Time/Urgency
🧠 AI/Intelligence
🚚 Vehicle/Transport
🌤️ Weather
🔍 Details/Inspection
🎯 Priority/Target
✅ Accept/Success
⏸️ Hold/Pause
⚠️ Override/Warning
🔴 Overridden/Alert
🟢 Low Risk
🟡 Medium Risk
🔴 High Risk
📋 List/Breakdown
🔧 Technical/Settings
📈 Chart/Growth
💡 Info/Insight
⚖️ Governance/Compliance
```

---

## 📱 Responsive Breakpoints

```css
/* Desktop (default) */
Layout: 2-column, wide margins

/* Tablet (if implemented) */
Layout: 2-column, reduced margins

/* Mobile (if implemented) */
Layout: Single column, full width
```

---

## ♿ Accessibility

### Contrast Ratios
- Primary text on white: 12.5:1 (AAA)
- Secondary text on white: 4.9:1 (AA)
- Risk badges: All pass WCAG AA

### Focus States
- Visible focus ring on all interactive elements
- Tab order follows visual hierarchy

### ARIA Labels
- All form inputs have labels
- Icon buttons have aria-labels
- Tables have proper headers

---

## 🔄 Animation Guidelines

**Currently: NO ANIMATIONS**

If added in future:
- Max duration: 200ms
- Easing: ease-in-out
- Only for state transitions
- Never for decorative purposes

---

## 📏 Layout Grid

### Seller View
```
┌─────────────────────┬──────────┐
│   Input Form        │  Help    │
│   (66% width)       │  (33%)   │
└─────────────────────┴──────────┘
┌──────────────────────────────────┐
│   AI Recommendation (full width) │
└──────────────────────────────────┘
```

### Manager View
```
┌──────────────────────────────────┐
│   Shipment Snapshot (6 tiles)    │
└──────────────────────────────────┘
┌──────────────────────────────────┐
│   AI Insight Panel               │
└──────────────────────────────────┘
┌─────────────────────┬──────────┐
│   Decision Panel    │  Guide   │
│   (66% width)       │  (33%)   │
└─────────────────────┴──────────┘
```

### Supervisor View
```
┌────┬────┬────┬────┐
│ M1 │ M2 │ M3 │ M4 │  (Metrics - 4 columns)
└────┴────┴────┴────┘
┌──────────┬──────────┐
│ Chart 1  │ Chart 2  │  (Analytics - 2 columns)
└──────────┴──────────┘
┌──────────────────────┐
│ Override Table       │  (Full width)
└──────────────────────┘
┌──────────┬──────────┐
│ Model    │ Features │  (Transparency - 2 columns)
└──────────┴──────────┘
```

---

## 🎨 CSS Variables Reference

```css
:root {
    /* Colors */
    --bg-color: #FAFAFA;
    --card-bg: #FFFFFF;
    --text-primary: #2E2E2E;
    --text-secondary: #6B7280;
    --border-color: #E5E7EB;
    --shadow: 0 1px 3px rgba(0,0,0,0.08);
    
    /* Spacing */
    --spacing-sm: 0.5rem;
    --spacing-md: 1rem;
    --spacing-lg: 1.5rem;
    
    /* Typography */
    --font-base: 0.9rem;
    --font-weight-normal: 400;
    --font-weight-semibold: 600;
    --font-weight-bold: 700;
    
    /* Border Radius */
    --radius-sm: 4px;
    --radius-md: 6px;
    --radius-lg: 8px;
}
```

---

## ✅ Design Checklist

Before deploying any UI changes, verify:

- [ ] Light theme only (no dark backgrounds)
- [ ] Soft risk colors (no harsh reds)
- [ ] Adequate whitespace
- [ ] Clear text hierarchy
- [ ] Readable font sizes (min 14px)
- [ ] High contrast ratios
- [ ] Consistent spacing
- [ ] Proper card styling
- [ ] Section headers present
- [ ] No unnecessary animations
- [ ] Progressive disclosure for technical details
- [ ] Governance hints where needed
- [ ] Mobile-friendly (if applicable)
- [ ] Accessible to screen readers

---

*Style Guide Version: 2.0*  
*Last Updated: January 11, 2026*  
*Maintained by: LICS Development Team*
