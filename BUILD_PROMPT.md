# CarbonBuddy V1 — Complete Build Prompt

## WHY — The Problem We're Solving

### The Core Insight
People want to contribute to reducing global warming, but when they start taking action, **they feel like they're doing it alone**. This feeling of isolation leads to:
- Loss of motivation after initial enthusiasm
- Uncertainty about what actions to take
- No sense of progress or impact
- Abandonment of climate-positive habits

### The Inspiration
The app is inspired by **Indore's transformation** from India's dirtiest to cleanest city through three key principles:
1. **Visible Progress** — Citizens could SEE the change happening
2. **Simple Rules** — Clear, actionable tasks anyone could follow
3. **Community Competition** — Healthy rivalry between neighborhoods fueled engagement

### The Gap in Existing Apps
Most carbon tracking apps answer "What's my footprint?" but fail to answer **"What do I do about it?"** — especially for users who don't know where to start.

---

## WHAT — The Solution (V1: "The Daily Nudge")

### Product Vision
**"Strava for climate action"** — Transform climate consciousness into a community-driven habit game.

### Core User Flow
```
Onboard → Get personalized daily checklist → Log tasks with specifics → 
Streak grows → See leaderboard → Feel community → Come back tomorrow
         ↑                                                          |
         └─── Chat: "I hate cooking" → Checklist adapts ───────────┘
```

### Three-Tab Architecture

#### 1. **Today Tab** — The Home Screen
**Purpose:** Turn awareness into daily action

**Components:**
- **Streak Header**
  - Fire emoji + day count (e.g., "Day 12 🔥")
  - Progress fraction (e.g., "3/5 done")
  - Encouraging message based on progress:
    - 0 tasks: "Pick any task that fits your day"
    - 1 task: "Great start! Every action counts"
    - 2 tasks: "Nice momentum! Keep it up"
    - 3+ tasks: "Streak secured! You're on a roll"
  - Streak shield badge (appears at 7+ day streak)

- **Progress Bar**
  - Gradient fill (orange → green) showing % completion

- **Daily Checklist (5 tasks)**
  - Tasks are **expandable** — click to reveal quantity input
  - Each task shows:
    - Checkbox/checkmark when done
    - Task text (e.g., "Take transit instead of driving")
    - Default CO2 saved (e.g., "2.4 kg")
    - Swap button (⇄) to replace with different task from same category
  - When expanded:
    - Quantity input field (pre-filled with default)
    - Live CO2 calculation preview (updates as you type)
    - "Log it" button
  - After logging:
    - Shows specifics (e.g., "Take transit · 30 km")
    - Displays instant feedback (e.g., "Logged! Saved driving 11 km in a car")
    - Task marked as complete with recalculated CO2

- **Footer**
  - Before logging: "Do what fits your day. Even 1 task makes a difference."
  - After logging: "You saved **[equivalency]** today"

- **Weekly Summary Button**
  - Dashed border button to view progress card

**Task Generation Logic:**
- 5 tasks per day from 4 categories: Transport, Food, Energy, Lifestyle
- Task mix based on onboarding profile:
  - Car commuter: 2 transport + 1 food + 1 energy + 1 lifestyle
  - Meat-heavy diet: 1 transport + 2 food + 1 energy + 1 lifestyle
  - Already green (bike + vegan): 1 transport + 1 food + 1 energy + 2 lifestyle
  - Transit user: 1 transport + 2 food + 1 energy + 1 lifestyle
- Tasks rotate daily using deterministic seed (day of year)
- 10-15 task variations per category to prevent repetition

#### 2. **Ranks Tab** — The Leaderboard
**Purpose:** Create community proof and healthy competition

**Components:**
- **Header**
  - "847 people saving together"
  - "Ranked by streak length"

- **Filter Toggle**
  - Global / [User's City] (e.g., Pittsburgh)

- **Leaderboard Table**
  - Columns: Rank # | Name | Streak (days) | CO2 Saved
  - Top 3 highlighted in light blue
  - **"You" row** highlighted in orange with thick border
  - Milestone badges next to names:
    - 7 days: Blue badge "7"
    - 30 days: Orange badge "30"
    - 100 days: Red badge "C"
  - CO2 shown in **human-readable equivalencies** (not kg):
    - < 1 kg: "charging your phone X times"
    - 1-5 kg: "driving X km in a car"
    - 5-20 kg: "powering your home for X days"
    - 20-100 kg: "X round-trip flights PIT-NYC"
    - 100+ kg: "X weeks of avg. emissions"
  - If user is ranked below #10, show:
    - Top 8 users
    - "..." divider
    - User's context (rank before, user, rank after)

- **Mock Data**
  - 16+ fake users with realistic names, streaks, and cities
  - User entry calculated from **actual logged CO2**, not approximation

#### 3. **Chat Tab** — The Plan Customizer
**Purpose:** Make the checklist adaptive to user's life

**Two Modes:**

**Mode 1 — Plan Customization (keyword detection):**
- User: "I work from home on Fridays"
- App: "Got it! I'll adjust your daily plan based on that. Your checklist will reflect this change starting tomorrow."
- Keywords: "work from home", "I'm vegan", "I can't", "I hate", "skip", "on fridays", etc.

**Mode 2 — Habit Logging (fallback to LLM):**
- User: "I biked to campus today"
- App: [Passes to backend LLM for response]

**UI:**
- Chat bubbles (user: blue right-aligned, assistant: white left-aligned with blue left border)
- Input field at bottom with "Send" button
- Hint text when empty:
  - "Tell me about your habits and I'll adjust your daily tasks."
  - Example prompts: "I work from home on Fridays", "I'm already vegan", "I biked to campus today"

### Gamification System

**Streak Logic:**
- **Threshold:** Complete 3 of 5 tasks = streak continues
- **Increment:** +1 day when threshold met (only once per day)
- **Streak Shield:** At 7+ day streak, get 1 free miss per week
  - Automatically applied if you miss a day
  - Resets every 7 streak days
- **Reset:** Falls to 0 if you miss >1 day without shield

**Milestones:**
- 7 days: Blue badge
- 30 days: Orange badge
- 100 days: Red "C" badge (Century)

**Weekly Summary Card (Modal):**
- Appears when clicking "View your weekly summary"
- Shows:
  - Current streak count
  - Tasks completed / total tasks
  - CO2 avoided in human-readable units
  - Community contribution: "Together, 847 people erased [equivalency] this week. You contributed X% of that."
- "Keep going" button to close

### Onboarding Survey (5 Steps)

**Step 1:** Welcome screen
- Title: "Let's speedrun your carbon baseline"
- Subtitle: "5 quick questions. No judgment. Just data."

**Step 2:** Location
- City (text input)
- Country (text input)

**Step 3:** Commute
- Mode: Car (solo) / Public transit / Bike or Walk / Remote work (tile select)
- If not remote: Distance slider (1-100 km/day)

**Step 4:** Diet
- Meat lover / Flexitarian / Vegetarian / Vegan (tile select)

**Step 5:** Home Energy
- Has AC in summer (checkbox)
- Has heating in winter (checkbox)

**Step 6:** Calculate Baseline
- Backend call to `/api/onboard-quick` with survey data
- Fallback: Client-side estimation if backend fails
- Shows:
  - Annual CO2 (e.g., "8,500 kg CO2/year")
  - Weekly average (e.g., "~163 kg/week")
  - Breakdown pie chart: Transport %, Food %, Energy %, Other %

**Step 7:** Set Weekly Goal
- Slider to set CO2 reduction target (5-25% of weekly baseline)
- Shows reduction percentage
- Default: 10% of weekly baseline

---

## HOW — Technical Implementation

### Tech Stack

**Frontend:**
- **Single HTML file** with embedded React 18 + Babel + CSS
- No build step, no npm packages, runs via CDN imports
- React via `<script>` tags (production builds from unpkg.com)
- Babel Standalone for JSX transformation
- All state managed with React hooks + localStorage

**Backend:**
- **FastAPI** (Python)
- **Claude Sonnet 4.5** via Dedalus Labs API (OpenAI-compatible client)
- **In-memory storage** (no database for V1 demo)
- Pre-seeded stats: 48,520 kg CO2, 847 users, 8,942 actions

**State Persistence:**
- localStorage with namespaced keys:
  - `carbonbuddy_user_id`: Unique user identifier
  - `carbonbuddy_onboarding_complete`: Boolean flag
  - `carbonbuddy_user_profile`: Survey data + baseline
  - `carbonbuddy_today`: { date, completed: [taskIds] }
  - `carbonbuddy_logged`: { date, data: { taskId: { qty, co2 } } }
  - `carbonbuddy_streak`: { currentStreak, lastDate, shieldAvailable, shieldUsedThisWeek }
  - `carbonbuddy_weekly`: { tasksCompleted, totalTasks, co2Saved }

### File Structure

```
carb-off/
├── frontend/
│   └── index.html          # Complete SPA (1850+ lines)
├── backend/
│   ├── main.py             # FastAPI server (575 lines)
│   └── emission_factors.json  # CO2 data for 25+ actions
├── .env                    # DEDALUS_API_KEY
└── start.sh                # Launch script for both servers
```

### Frontend Architecture (index.html)

**CSS Variables (Design System):**
```css
--primary-blue: #3B82F6
--accent-green: #10B981
--streak-orange: #F59E0B
--bg-light: #F8FAFC
--surface-white: #FFFFFF
--text-primary: #1E293B
--text-secondary: #64748B
/* + spacing, radius, shadow tokens */
```

**React Component Tree:**
```
App
├── OnboardingSurvey (7 steps)
├── Tabs (Today | Ranks | Chat)
├── TodayTab
│   ├── StreakHeader
│   ├── ProgressBar
│   ├── Checklist (5 tasks)
│   └── WeeklySummaryButton
├── RanksTab
│   ├── LeaderboardHeader
│   ├── FilterToggle (Global/City)
│   └── LeaderboardTable
├── ChatTab
│   ├── Messages
│   └── InputContainer
└── WeeklySummary (modal)
```

**Key State Variables:**
```javascript
const [activeTab, setActiveTab] = useState('today')
const [userId, setUserId] = useState(null)
const [userProfile, setUserProfile] = useState(null)
const [dailyTasks, setDailyTasks] = useState([])
const [completedTasks, setCompletedTasks] = useState([])
const [loggedData, setLoggedData] = useState({}) // { taskId: { qty, co2 } }
const [streak, setStreak] = useState(loadStreakData())
const [weeklyStats, setWeeklyStats] = useState(loadWeeklyStats())
const [messages, setMessages] = useState([])
```

**Task Pool Structure:**
```javascript
const TASK_POOL = {
  transport: [
    { 
      id: 't1', 
      text: 'Take transit instead of driving',
      co2PerUnit: 0.12,  // kg per km
      defaultQty: 20,     // default km
      unit: 'km',
      co2: 2.4            // default total
    },
    // ... more transport tasks
  ],
  food: [ /* ... */ ],
  energy: [ /* ... */ ],
  lifestyle: [ /* ... */ ]
}
```

**Critical Functions:**

1. **generateDailyTasks(profile):**
   - Returns 5 tasks based on user's commute mode + diet
   - Uses day-of-year as deterministic seed for rotation
   - Mixes categories per profile template

2. **handleLogTask(taskId, qty, co2):**
   - Marks task as completed
   - Saves logged quantity + CO2 to state + localStorage
   - Updates `weeklyStats.co2Saved` (reactive!)
   - Increments streak if threshold (3/5) met
   - Triggers re-render → leaderboard updates instantly

3. **handleUndoTask(taskId):**
   - Removes from completed list
   - Deletes logged data
   - Subtracts CO2 from weekly stats
   - Saves to localStorage

4. **handleSwapTask(taskId):**
   - Finds task's category (transport/food/energy/lifestyle)
   - Filters for unused tasks in same category
   - Randomly picks one replacement
   - Replaces in dailyTasks array
   - Cleans up if task was already completed

5. **getEquivalency(kgCo2):**
   - Returns human-readable string based on CO2 amount
   - Tiered thresholds for different units

### Backend Architecture (main.py)

**API Endpoints:**

1. **POST `/api/onboard-quick`**
   - Input: `{ user_id, city, country, commuteMode, commuteDistance, foodVibe, hasAC, hasHeating }`
   - Calculates baseline annual + weekly CO2
   - Returns: `{ baseline: { annual, weekly, breakdown } }`
   - Estimation logic:
     - Base: 3000 kg/year
     - Car commute: +0.2 kg/km/day * 250 days
     - Transit: +0.05 kg/km/day * 250 days
     - Meat diet: +2500 kg
     - Flexitarian: +1800 kg
     - Vegetarian: +1200 kg
     - Vegan: +800 kg
     - AC: +500 kg
     - Heating: +1000 kg

2. **POST `/api/log`**
   - Input: `{ user_id, message }`
   - Sends message to Claude via Dedalus API
   - Returns: `{ response_text, co2_logged }`
   - System prompt guides Claude to extract actions + calculate CO2

3. **GET `/api/stats/global`**
   - Returns: `{ total_co2_saved_kg, active_users, timestamp }`
   - Pre-seeded values for demo

4. **GET `/api/dashboard/{user_id}`**
   - Returns user's action history
   - Pre-seeded with mock data for demo

**Claude Integration:**
```python
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("DEDALUS_API_KEY"),
    base_url="https://api.dedalus.ai/v1"
)

response = client.chat.completions.create(
    model="anthropic/claude-sonnet-4-5-20250929",
    messages=[...]
)
```

### Setup & Run Instructions

**Prerequisites:**
- Python 3.9+
- Modern browser (Chrome, Firefox, Safari)

**Step 1: Clone/Setup**
```bash
# Create project structure
mkdir carb-off
cd carb-off
mkdir frontend backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn python-dotenv openai
```

**Step 2: Create `.env` file**
```
DEDALUS_API_KEY=your_api_key_here
```

**Step 3: Add emission_factors.json**
```json
{
  "food": {
    "beef_meal": { "co2_kg": 3.7, "description": "One beef-heavy meal" },
    "vegetarian_meal": { "co2_kg": 1.0, "description": "One vegetarian meal" }
  },
  "transport": {
    "car_km": { "co2_kg": 0.21, "description": "Car (solo) per km" },
    "transit_km": { "co2_kg": 0.05, "description": "Public transit per km" }
  },
  "home_energy": {
    "ac_hour": { "co2_kg": 0.46, "description": "AC per hour" },
    "cold_wash": { "co2_kg": 0.6, "description": "Cold vs hot wash" }
  },
  "lifestyle": {
    "reusable_bottle": { "co2_kg": 0.082, "description": "Skip disposable bottle" },
    "plastic_bag": { "co2_kg": 0.033, "description": "Reusable vs plastic bag" }
  }
}
```

**Step 4: Create start.sh**
```bash
#!/bin/bash
# Kill existing processes
lsof -ti:8000 -ti:3000 2>/dev/null | xargs kill 2>/dev/null

# Start backend
source venv/bin/activate
cd backend
python3 main.py &

# Start frontend
sleep 2
cd ../frontend
python3 -m http.server 3000 &

echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:3000"
```

**Step 5: Run**
```bash
chmod +x start.sh
./start.sh
```

**Step 6: Open Browser**
- Navigate to `http://localhost:3000`
- Complete onboarding survey
- Start logging tasks!

### Design Principles

**1. No Pressure, Just Progress:**
- Never force users to complete all tasks
- Celebrate any action: "Even 1 task makes a difference"
- Progressive encouragement, not guilt

**2. Specificity Builds Trust:**
- Users can input exact quantities (30 km, 10 floors)
- Instant feedback with recalculated CO2
- Human-readable equivalencies (not raw kg)

**3. Community Without Social Proof Anxiety:**
- Leaderboard shows you're part of something bigger
- Your row is highlighted, but you're not shamed for low rank
- City filter lets you compete locally if global is intimidating

**4. Reactive Everything:**
- Log task → CO2 updates in footer, weekly card, AND leaderboard
- Swap task → new task appears instantly
- No loading spinners, no delays

**5. Beautiful Minimalism:**
- 3 tabs, not 6
- Each screen has ONE job
- Premium feel: smooth gradients, subtle shadows, modern typography (Space Grotesk)

### Edge Cases & Gotchas

**1. Streak Continuity:**
- If app is opened after missing 1 day, streak resets UNLESS shield is available
- Shield only applies once per week
- Streak only increments once per day (even if you log multiple times)

**2. Daily Task Reset:**
- Tasks are deterministic based on day-of-year
- Same user sees same tasks if they refresh on the same day
- Completed status is preserved in localStorage

**3. Weekly Stats Reset:**
- Currently manual — would need backend cron job in production
- For demo, weekly stats accumulate indefinitely

**4. Backend Failure Handling:**
- Onboarding: Falls back to client-side baseline calculation
- Chat: Shows error message if API call fails
- Stats: Returns pre-seeded values if no data

**5. Browser Compatibility:**
- Requires ES6+ support (arrow functions, destructuring, spread)
- localStorage must be enabled
- Works on all modern browsers (Chrome 90+, Firefox 88+, Safari 14+)

---

## Success Criteria

A successful V1 build should have:

✅ **Onboarding completes in under 2 minutes**
✅ **Daily checklist shows 5 personalized tasks**
✅ **Tasks can be logged with custom quantities (e.g., "30 km")**
✅ **Streak counter increments when 3/5 tasks are completed**
✅ **Leaderboard shows user's actual CO2 saved, not hardcoded approximation**
✅ **Leaderboard updates reactively when tasks are logged**
✅ **Chat detects plan customization keywords and confirms adaptation**
✅ **Weekly summary shows accurate accumulated CO2 + community contribution**
✅ **All CO2 displayed in human-readable units (no raw kg)**
✅ **Swap button replaces task with different one from same category**
✅ **Frontend works as a single HTML file with no build step**
✅ **Backend runs on port 8000, frontend on port 3000**

---

## Future Enhancements (Post-V1)

*Not included in this build, but directionally important:*

- **Real database** (PostgreSQL) to persist user data across sessions
- **User authentication** (social login)
- **Weekly stats auto-reset** (cron job every Sunday)
- **Community challenges** (e.g., "50 people do transit week")
- **Share cards** (auto-generated images for social media)
- **NGO dashboards** (aggregate impact for partner organizations)
- **Mobile app** (React Native wrapper)
- **AI-generated task customization** (Claude modifies TASK_POOL based on chat)

---

## Final Note

This app is not about guilt or perfection. It's about **making climate action feel like a game you play with your community**, where even small actions add up to visible impact. The goal is to answer the question: **"What if caring about the planet felt like leveling up in a game?"**

Now go build it. 🌍🚀
