# CarbonBuddy Redesign - Premium Dark Theme

## Design Inspiration: Cool The Globe

### Color Palette
```css
--bg-dark: #0F1419;           /* Near black background */
--bg-card: #1C2127;            /* Card background */
--bg-surface: #252C34;         /* Elevated surfaces */

--accent-mint: #4FFFB0;        /* Primary mint green */
--accent-teal: #00CFC1;        /* Secondary teal */
--accent-dark-teal: #1A4D3E;   /* Dark teal for cards */

--text-primary: #FFFFFF;       /* Main text */
--text-secondary: #9BA3AF;     /* Secondary text */
--text-muted: #6B7280;         /* Muted text */
```

### Key Components to Redesign

#### 1. **Top Bar**
- Dark background with subtle border
- Logo on left: "CARBONBUDDY" with green accent on "BUDDY"
- Stats badges in center (streak, CO2 saved)
- Profile avatar on right

#### 2. **Navigation**
- **Bottom navigation** (like Cool The Globe)
- Left: Home icon (mint when active)
- Center: Floating circular button with wave icon
- Right: Community/Ranks icon

#### 3. **Today Tab** → Redesigned as "Home"
- **Hero Card:** Large image card with "Let's Start With Action 🏆"
- **Segmented Control:** Personal / Community / Global (pill-shaped)
- **Task Cards:** Dark cards with:
  - Left: Icon/emoji
  - Center: Task description
  - Right: CO2 badge + chevron
  - When tapped: expand with quantity input

#### 4. **Ranks Tab** → "Community"
- **Hero Section:** Total community impact
- **Leaderboard Cards:** Individual cards for each user
  - Profile picture (generated gradient)
  - Name + City
  - Streak badge
  - CO2 saved in large text

#### 5. **Chat Tab** → Integrated into floating button
- Opens as modal overlay
- Dark background with mint green accents
- Better message bubbles

### Layout Changes

**Before (3 tabs at top):**
```
[Today | Ranks | Chat]
─────────────────────
Content area
```

**After (Bottom nav + floating action):**
```
Content area
(more screen space!)
─────────────────────
[Home]  [Ⓒ Action]  [Community]
```

### Typography
- Headings: Space Grotesk 700 (bold)
- Body: Space Grotesk 400/500
- Numbers: Space Grotesk 600 (tabular)

### Visual Enhancements

1. **Glassmorphism** on cards
2. **Gradient overlays** on images
3. **Floating shadows** for depth
4. **Micro-animations** on interactions
5. **Progress rings** instead of bars
6. **Badge pills** for stats
7. **Rounded corners** everywhere (16px+)

### Implementation Plan

**Phase 1: Color System**
- Update CSS variables to dark theme
- Add new accent colors

**Phase 2: Navigation**
- Move tabs to bottom
- Add floating center button
- Implement smooth transitions

**Phase 3: Today Tab (Home)**
- Add hero card with image
- Redesign task cards
- Add segmented control

**Phase 4: Ranks Tab (Community)**
- Card-based leaderboard
- Better visual hierarchy
- Add profile avatars

**Phase 5: Chat Integration**
- Modal overlay from floating button
- Better message styling

Need user approval before proceeding with full redesign as it's a major visual overhaul.
