# Chat-Based Ad-Hoc Logging — How It Works

## Overview
The Chat tab now supports logging ANY climate action you take, not just the tasks in your daily checklist. The app will extract the action, calculate CO2 savings, and update your leaderboard in real-time.

## How to Use

### 1. Go to the Chat Tab
Click the "Chat" tab in the main app.

### 2. Describe What You Did
Type natural language messages describing your actions:

**Examples:**
- "I biked 15 km to campus today"
- "I had a vegetarian lunch"
- "I took the bus instead of driving 10 km"
- "I turned off the AC for 3 hours"
- "I did a cold wash laundry"

### 3. The App Will:
1. **Extract the action** using Claude AI
2. **Calculate CO2 saved** by comparing to your baseline from onboarding
3. **Update `weeklyStats.co2Saved`** immediately
4. **Update the leaderboard** reactively (your "You" row updates instantly)
5. **Show a green confirmation** message: "✅ Logged! Your leaderboard rank just updated."

## How CO2 Is Calculated

The backend compares your action to **your baseline** (from the onboarding survey):

### Transport Actions
- **Your Baseline:** The commute mode you selected (Car, Transit, Bike, Remote)
- **Calculation:** CO2 saved = (baseline emissions - actual emissions) * distance
- **Example:** 
  - Baseline: Car (solo) = 0.21 kg/km
  - Action: Took bus 10 km = 0.05 kg/km
  - Saved: (0.21 - 0.05) * 10 = **1.6 kg CO2**

###Food Actions
- **Your Baseline:** The diet you selected (Meat lover, Flexitarian, Vegetarian, Vegan)
- **Calculation:** CO2 saved = (baseline emissions - actual emissions) * meals
- **Example:**
  - Baseline: Meat lover = 3.7 kg/meal
  - Action: Vegetarian meal = 1.0 kg/meal
  - Saved: 3.7 - 1.0 = **2.7 kg CO2**

### Energy & Lifestyle Actions
- **No Baseline Needed:** These are inherently savings
- **Examples:**
  - Turn off AC for 1 hour = **0.46 kg CO2**
  - Cold wash instead of hot = **0.6 kg CO2**
  - Reusable bottle vs disposable = **0.082 kg CO2**

## Important Notes

### ⚠️ Zero Savings Scenarios
If you log an action that **matches your baseline**, you'll save 0 CO2:

- **Example 1:** If your commute mode is "Bike", logging "I biked 20 km" saves 0 kg (bike vs bike)
- **Example 2:** If your diet is "Vegan", logging "I had a vegan meal" saves 0 kg (vegan vs vegan)

**Claude will respond:** "That's your usual — keeping it consistent!"

This is **correct behavior**. The app rewards you for doing *better* than your normal habits.

### ✅ To Get CO2 Savings
Log actions that are **better than your baseline**:

- **If your baseline is Car:** Log taking transit, biking, carpooling
- **If your baseline is Meat lover:** Log vegetarian or vegan meals
- **If your baseline is Transit:** Log biking or walking
- **Energy actions always count:** Turning off AC, cold wash, etc.

## Technical Flow

### Frontend (`index.html`)
```javascript
// In handleSend (Chat tab)
if (data.total_saved_today && data.total_saved_today > 0) {
    const newWeekly = { ...weeklyStats };
    newWeekly.co2Saved += data.total_saved_today;
    setWeeklyStats(newWeekly);
    saveWeeklyStats(newWeekly);
    
    // Show green confirmation after 800ms
    setTimeout(() => {
        setMessages(prev => [...prev, {
            role: 'system',
            content: `✅ Logged! Your leaderboard rank just updated.`,
            isSystem: true
        }]);
    }, 800);
}
```

### Backend (`main.py`)
```python
# 1. Claude extracts action details
classified_actions = [
    {
        "category": "transport",
        "action_type": "bike_walk",
        "quantity": 20,
        "unit": "km",
        "confidence": "high"
    }
]

# 2. Calculate savings vs baseline
baseline_type = user.get("commute_mode", "car_petrol")  # e.g., "bike_walk"
baseline_factor = EMISSION_FACTORS[baseline_type]       # e.g., 0.0 kg/km
actual = emission_factor * quantity                     # 0.0 * 20 = 0
baseline = baseline_factor * quantity                   # 0.0 * 20 = 0
saved = max(0, baseline - actual)                       # 0 kg

# 3. Return response
return {
    "response_text": "That's your usual — keeping it consistent!",
    "total_saved_today": 0.0,  # No state update
    "actions_logged": [...]
}
```

## Testing the Feature

### Test Case 1: Save CO2 (Car → Bike)
**Setup:** Onboarding with "Car (solo)" as commute mode

**Action:** "I biked 25 km today"

**Expected:**
- Backend calculates: (0.21 - 0.0) * 25 = **5.25 kg saved**
- Response: "Amazing! You saved 5.2 kg of CO2 today — that's like... [equivalency]. Together with the community..."
- Green confirmation appears: "✅ Logged! Your leaderboard rank just updated."
- Leaderboard "You" row updates from "charging your phone 0 times" → "driving 19 km in a car"

### Test Case 2: Zero Savings (Bike → Bike)
**Setup:** Onboarding with "Bike/Walk" as commute mode

**Action:** "I biked 20 km today"

**Expected:**
- Backend calculates: (0.0 - 0.0) * 20 = **0 kg saved**
- Response: "That's your usual — keeping it consistent! 🚴 Every kilometer you bike..."
- NO green confirmation (because `total_saved_today === 0`)
- Leaderboard stays unchanged

### Test Case 3: Vegetarian Meal (Meat → Veggie)
**Setup:** Onboarding with "Meat lover" as diet

**Action:** "I had a vegetarian lunch"

**Expected:**
- Backend calculates: (3.7 - 1.0) * 1 = **2.7 kg saved**
- Response with CO2 amount and equivalency
- Green confirmation appears
- Leaderboard updates

## Troubleshooting

### Issue: No response in chat
**Cause:** Backend API key not set or server down
**Fix:** Check `.env` file has `DEDALUS_API_KEY` and backend is running on port 8000

### Issue: Response says "That's your usual" but I expected savings
**Cause:** Your logged action matches your baseline from onboarding
**Fix:** Log actions that are *better* than your normal habits (see examples above)

### Issue: Green confirmation never appears
**Cause:** `total_saved_today` is 0 or negative
**Fix:** Verify your action saves CO2 vs your baseline

### Issue: Leaderboard doesn't update
**Cause:** State update only happens if `total_saved_today > 0`
**Fix:** Same as above — ensure you're logging actions better than your baseline

## Future Enhancements

- [ ] Add visual preview in chat showing "You'll save X kg CO2 from this action"
- [ ] Show breakdown of all actions logged today in a summary card
- [ ] Allow editing/deleting ad-hoc logged actions
- [ ] Sync ad-hoc actions to backend database for persistence
- [ ] Add auto-suggestions based on common patterns ("Did you mean...?")
- [ ] Show streak progress from chat actions (currently only daily tasks count toward streak)
