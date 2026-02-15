from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json
import uuid
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="CarbonBuddy API")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database (for hackathon - replace with real DB for production)
users_db = {}
actions_db = []
global_stats = {
    "total_co2_saved_kg": 48520.3,
    "total_actions_logged": 8942,
    "total_users": 847,
    "last_updated": datetime.now().isoformat()
}

# Load emission factors
with open('emission_factors.json', 'r') as f:
    emission_data = json.load(f)
    EMISSION_FACTORS = {f['action_type']: f for f in emission_data['factors']}
    EQUIVALENCIES = emission_data['equivalencies']

# Initialize Dedalus client (OpenAI-compatible)
client = OpenAI(
    api_key=os.environ.get("DEDALUS_API_KEY", ""),
    base_url="https://api.dedaluslabs.ai/v1"
)

# Pydantic models
class OnboardMessage(BaseModel):
    user_id: str
    message: str

class LogMessage(BaseModel):
    user_id: str
    message: str

class UserProfile(BaseModel):
    user_id: str
    display_name: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None
    commute_distance_km: Optional[float] = 0
    commute_mode: Optional[str] = "car_petrol"
    diet_type: Optional[str] = "meat_mixed_meal"
    meals_per_day: int = 3
    has_ac: bool = False
    heating_type: Optional[str] = None
    estimated_annual_footprint_kg: Optional[float] = None
    onboarding_complete: bool = False
    conversation_history: List[Dict[str, str]] = []

class QuickOnboardData(BaseModel):
    user_id: str
    city: str
    country: Optional[str] = None
    commuteMode: str
    commuteDistance: int
    foodVibe: str
    hasAC: bool
    hasHeating: bool

def get_equivalency(kg_co2: float) -> str:
    """Get tangible equivalency for carbon amount"""
    thresholds = sorted([float(k) for k in EQUIVALENCIES.keys()], reverse=True)
    for threshold in thresholds:
        if kg_co2 >= threshold:
            return EQUIVALENCIES[str(int(threshold))]
    return EQUIVALENCIES["1"]

def calculate_annual_footprint(profile: UserProfile) -> float:
    """Calculate estimated annual footprint from profile"""
    # Transport (250 work days)
    commute_factor = EMISSION_FACTORS.get(profile.commute_mode, EMISSION_FACTORS["car_petrol"])
    transport_annual = profile.commute_distance_km * 2 * 250 * commute_factor["emission_factor_kg_co2e"]
    
    # Food (365 days)
    food_factor = EMISSION_FACTORS.get(profile.diet_type, EMISSION_FACTORS["meat_mixed_meal"])
    food_annual = food_factor["emission_factor_kg_co2e"] * profile.meals_per_day * 365
    
    # Home energy (rough estimate)
    home_annual = 1500  # Average US household baseline
    if profile.has_ac:
        home_annual += 500
    
    return transport_annual + food_annual + home_annual

@app.post("/api/onboard")
async def onboard(data: OnboardMessage):
    """Handle onboarding conversation"""
    user_id = data.user_id
    
    # Initialize or get user
    if user_id not in users_db:
        users_db[user_id] = UserProfile(user_id=user_id).dict()
    
    user = users_db[user_id]
    user["conversation_history"].append({"role": "user", "content": data.message})
    
    # Onboarding prompt
    onboarding_prompt = """You are CarbonBuddy, a friendly AI climate coach. You are onboarding a new user.
Your job is to have a SHORT, natural 2-minute conversation to learn about their lifestyle so you can calculate their carbon baseline.

You need to collect:
1. Their city/country (for location-specific emission factors)
2. How they typically commute and approximate distance (one-way in km or miles)
3. Their general diet pattern (how many days per week they eat meat)
4. Whether they use AC or heating regularly

RULES:
- Ask ONE question at a time
- Keep it conversational — not a survey
- Be warm, not preachy
- If user mentions they don't commute or work from home, set commute to 0
- After collecting all 4 pieces of info, calculate their estimated annual footprint

ANNUAL FOOTPRINT ESTIMATE:
= (commute_emissions_per_day × 250 work days)
+ (food_emissions_per_day × 365)
+ (home_energy_estimate × 365)

After presenting the baseline, tell them their single biggest carbon source and say: 
"Now you can just text me anytime you make a climate-friendly choice and I'll track the impact. Try it — tell me what you did today."

When you have all the info, output ONLY a JSON block with:
{
  "onboarding_complete": true,
  "city": "...",
  "country": "...",
  "commute_distance_km": ...,
  "commute_mode": "car_petrol|bus|train_electric|bike_walk",
  "diet_type": "beef_heavy_meal|meat_mixed_meal|vegetarian_meal|vegan_meal",
  "meals_per_day": 3,
  "has_ac": true/false,
  "heating_type": "gas|electric|none",
  "display_name": "..."
}

If not complete yet, just respond conversationally."""
    
    # Call Claude via Dedalus
    messages = [{"role": "system", "content": onboarding_prompt}] + user["conversation_history"]

    try:
        response = client.chat.completions.create(
            model="anthropic/claude-sonnet-4-5-20250929",
            max_tokens=1000,
            messages=messages
        )

        response_text = response.choices[0].message.content
        user["conversation_history"].append({"role": "assistant", "content": response_text})
        
        # Check if onboarding is complete (look for JSON)
        if "{" in response_text and "onboarding_complete" in response_text:
            try:
                # Extract JSON
                json_start = response_text.index("{")
                json_end = response_text.rindex("}") + 1
                profile_data = json.loads(response_text[json_start:json_end])
                
                if profile_data.get("onboarding_complete"):
                    # Update user profile
                    user.update(profile_data)
                    
                    # Calculate footprint
                    temp_profile = UserProfile(**user)
                    footprint = calculate_annual_footprint(temp_profile)
                    user["estimated_annual_footprint_kg"] = footprint
                    user["onboarding_complete"] = True
                    
                    # Add to global users count
                    global_stats["total_users"] += 1
                    
                    # Generate final response with footprint
                    final_response = f"Your estimated annual carbon footprint is {footprint:,.0f} kg CO2. "
                    
                    # Determine biggest source
                    sources = []
                    commute_factor = EMISSION_FACTORS.get(user["commute_mode"], EMISSION_FACTORS["car_petrol"])
                    transport_annual = user["commute_distance_km"] * 2 * 250 * commute_factor["emission_factor_kg_co2e"]
                    sources.append(("commute", transport_annual))
                    
                    food_factor = EMISSION_FACTORS.get(user["diet_type"], EMISSION_FACTORS["meat_mixed_meal"])
                    food_annual = food_factor["emission_factor_kg_co2e"] * user["meals_per_day"] * 365
                    sources.append(("food", food_annual))
                    
                    sources.sort(key=lambda x: x[1], reverse=True)
                    biggest = sources[0]
                    pct = (biggest[1] / footprint * 100) if footprint > 0 else 0
                    
                    final_response += f"Your biggest source is {biggest[0]} at {pct:.0f}%. Now you can just text me anytime you make a climate-friendly choice and I'll track the impact. Try it — tell me what you did today!"
                    
                    return {
                        "response_text": final_response,
                        "onboarding_complete": True,
                        "user_profile": user
                    }
            except (ValueError, json.JSONDecodeError) as e:
                # JSON extraction failed, continue conversation
                pass
        
        return {
            "response_text": response_text,
            "onboarding_complete": False
        }
        
    except Exception as e:
        # Fallback response if API fails
        print(f"ERROR in onboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "response_text": "I'm having trouble connecting right now. Let's try again - where are you located?",
            "onboarding_complete": False
        }

@app.post("/api/onboard-quick")
async def onboard_quick(data: QuickOnboardData):
    """Handle quick survey-based onboarding"""
    user_id = data.user_id

    # Map survey data to emission factor keys
    commute_mode_map = {
        "car": "car_petrol",
        "transit": "bus",
        "bike": "bike_walk",
        "remote": "bike_walk"  # No commute
    }

    food_map = {
        "meat": "beef_heavy_meal",
        "flex": "meat_mixed_meal",
        "veggie": "vegetarian_meal",
        "vegan": "vegan_meal"
    }

    # Create user profile
    commute_mode = commute_mode_map.get(data.commuteMode, "car_petrol")
    diet_type = food_map.get(data.foodVibe, "meat_mixed_meal")
    commute_distance = 0 if data.commuteMode == "remote" else data.commuteDistance

    profile = UserProfile(
        user_id=user_id,
        city=data.city,
        country=data.country,
        commute_distance_km=commute_distance,
        commute_mode=commute_mode,
        diet_type=diet_type,
        meals_per_day=3,
        has_ac=data.hasAC,
        heating_type="gas" if data.hasHeating else "none",
        onboarding_complete=True
    )

    # Calculate footprint
    footprint_annual = calculate_annual_footprint(profile)
    profile.estimated_annual_footprint_kg = footprint_annual

    # Store user profile
    users_db[user_id] = profile.dict()

    # Update global stats
    global_stats["total_users"] += 1

    # Calculate breakdown percentages
    commute_factor = EMISSION_FACTORS.get(commute_mode, EMISSION_FACTORS["car_petrol"])
    transport_annual = commute_distance * 2 * 250 * commute_factor["emission_factor_kg_co2e"]

    food_factor = EMISSION_FACTORS.get(diet_type, EMISSION_FACTORS["meat_mixed_meal"])
    food_annual = food_factor["emission_factor_kg_co2e"] * 3 * 365

    home_annual = 1500
    if data.hasAC:
        home_annual += 500

    total = transport_annual + food_annual + home_annual

    breakdown = {
        "transport": round((transport_annual / total * 100)) if total > 0 else 0,
        "food": round((food_annual / total * 100)) if total > 0 else 0,
        "energy": round((home_annual / total * 100)) if total > 0 else 0,
        "other": 0
    }

    # Adjust to ensure total is 100%
    breakdown["other"] = 100 - breakdown["transport"] - breakdown["food"] - breakdown["energy"]

    return {
        "baseline": {
            "annual": round(footprint_annual),
            "weekly": round(footprint_annual / 52),
            "breakdown": breakdown
        },
        "user_profile": users_db[user_id]
    }

@app.post("/api/log")
async def log_action(data: LogMessage):
    """Log climate actions"""
    user_id = data.user_id
    
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found. Please complete onboarding first.")
    
    user = users_db[user_id]
    
    if not user.get("onboarding_complete"):
        raise HTTPException(status_code=400, detail="Please complete onboarding first.")
    
    # Classification prompt
    classification_prompt = f"""You are parsing a user's natural language message to identify climate actions they took.

USER PROFILE:
{json.dumps(user, indent=2)}

USER MESSAGE:
"{data.message}"

YOUR TASK:
Extract every climate-relevant action from this message. For each action, output a structured classification.

OUTPUT FORMAT (JSON array only, no other text):
[
  {{
    "category": "food|transport|home_energy|lifestyle",
    "action_type": "<exact match from list below>",
    "quantity": <number>,
    "unit": "<meals|km|hours|loads|uses>",
    "confidence": "high|medium|low",
    "reasoning": "<brief explanation>"
  }}
]

VALID action_types:
FOOD: beef_heavy_meal, meat_mixed_meal, fish_meal, vegetarian_meal, vegan_meal
TRANSPORT: car_petrol, car_diesel, car_electric, bus, train_electric, bike_walk, carpool_2, carpool_3plus, flight_short, flight_long
HOME_ENERGY: ac_hour, heating_gas_hour, lights_off_hour, cold_wash, line_dry
LIFESTYLE: reusable_bottle, reusable_bag, no_food_waste, local_produce, secondhand_clothing, secondhand_electronics

RULES:
- For transport: if user mentions "work" or "commute" without distance, use their commute_distance_km: {user.get('commute_distance_km', 10)} km
- For carpooling: note the number of people
- If no climate-relevant action found, return: [{{"no_action": true}}]
- NEVER estimate carbon numbers. Only classify.
- Convert miles to km (1 mile = 1.6 km)
"""
    
    try:
        # Call Claude for classification via Dedalus
        response = client.chat.completions.create(
            model="anthropic/claude-sonnet-4-5-20250929",
            max_tokens=1000,
            messages=[
                {"role": "system", "content": classification_prompt},
                {"role": "user", "content": data.message}
            ]
        )

        response_text = response.choices[0].message.content
        
        # Extract JSON
        json_start = response_text.index("[")
        json_end = response_text.rindex("]") + 1
        classified_actions = json.loads(response_text[json_start:json_end])
        
        if len(classified_actions) == 1 and classified_actions[0].get("no_action"):
            return {
                "response_text": "I didn't catch a specific climate action in that message. Try telling me something like 'I took the bus today' or 'I had a veggie lunch'!",
                "actions_logged": [],
                "total_saved_today": 0,
                "global_stats": global_stats
            }
        
        # Calculate carbon savings for each action
        calculated_results = []
        total_saved = 0
        
        for action in classified_actions:
            action_type = action["action_type"]
            category = action["category"]
            quantity = action["quantity"]
            
            if action_type not in EMISSION_FACTORS:
                continue
            
            factor = EMISSION_FACTORS[action_type]
            emission_factor = factor["emission_factor_kg_co2e"]
            
            # Calculate baseline vs actual
            if category == "food":
                # Baseline is user's usual diet
                baseline_type = user.get("diet_type", "meat_mixed_meal")
                baseline_factor = EMISSION_FACTORS[baseline_type]["emission_factor_kg_co2e"]
                actual = emission_factor * quantity
                baseline = baseline_factor * quantity
                saved = max(0, baseline - actual)
                
            elif category == "transport":
                # Baseline is user's usual commute mode
                baseline_type = user.get("commute_mode", "car_petrol")
                baseline_factor = EMISSION_FACTORS[baseline_type]["emission_factor_kg_co2e"]
                actual = emission_factor * quantity
                baseline = baseline_factor * quantity
                saved = max(0, baseline - actual)
                
            else:
                # Home energy and lifestyle are already expressed as savings
                saved = emission_factor * quantity
                baseline = saved
                actual = 0
            
            total_saved += saved
            
            calculated_results.append({
                "action_type": action_type,
                "display_name": factor["display_name"],
                "quantity": quantity,
                "unit": factor["unit"],
                "co2_saved_kg": round(saved, 2),
                "source": factor["source"]
            })
            
            # Store in actions DB
            action_record = {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "logged_at": datetime.now().isoformat(),
                "category": category,
                "action_type": action_type,
                "quantity": quantity,
                "co2_saved_kg": saved
            }
            actions_db.append(action_record)
        
        # Update global stats
        global_stats["total_co2_saved_kg"] += total_saved
        global_stats["total_actions_logged"] += len(calculated_results)
        global_stats["last_updated"] = datetime.now().isoformat()
        
        # Generate friendly response
        response_prompt = f"""You are CarbonBuddy, a friendly AI climate coach. The user just logged action(s) and we've calculated the impact. Generate a response.

ACTIONS LOGGED AND CALCULATED:
{json.dumps(calculated_results, indent=2)}

COLLECTIVE STATS:
- Total CO2 saved by all users: {global_stats['total_co2_saved_kg']:.1f} kg
- User's total saved from this action: {total_saved:.1f} kg

RESPONSE RULES:
1. State the EXACT co2_saved_kg numbers. Use one decimal place.
2. Include ONE tangible equivalency: {get_equivalency(total_saved)}
3. Mention the collective impact naturally
4. Keep to 2-3 sentences. Be warm and specific.
5. Don't use more than one emoji
6. If co2_saved_kg is 0 or very small (<0.1), say "That's your usual — keeping it consistent!" instead of celebrating

Generate ONLY the response text, nothing else."""
        
        final_response = client.chat.completions.create(
            model="anthropic/claude-sonnet-4-5-20250929",
            max_tokens=500,
            messages=[
                {"role": "system", "content": response_prompt},
                {"role": "user", "content": "Generate the response"}
            ]
        )

        response_text = final_response.choices[0].message.content
        
        return {
            "response_text": response_text,
            "actions_logged": calculated_results,
            "total_saved_today": round(total_saved, 2),
            "global_stats": global_stats
        }
        
    except Exception as e:
        print(f"Error: {e}")
        return {
            "response_text": f"I had trouble processing that. Could you rephrase what you did today?",
            "actions_logged": [],
            "total_saved_today": 0,
            "global_stats": global_stats
        }

@app.get("/api/dashboard/{user_id}")
async def get_dashboard(user_id: str):
    """Get user dashboard data"""
    if user_id not in users_db:
        raise HTTPException(status_code=404, detail="User not found")
    
    user = users_db[user_id]
    
    # Get user's actions
    user_actions = [a for a in actions_db if a["user_id"] == user_id]
    total_saved = sum(a["co2_saved_kg"] for a in user_actions)
    
    # Calculate projected footprint
    estimated = user.get("estimated_annual_footprint_kg", 8200)
    if total_saved > 0 and len(user_actions) > 0:
        # Simple projection based on current rate
        days_active = len(set(a["logged_at"][:10] for a in user_actions))
        if days_active > 0:
            daily_avg_saved = total_saved / days_active
            annual_saved = daily_avg_saved * 365
            projected = max(0, estimated - annual_saved)
        else:
            projected = estimated
    else:
        projected = estimated
    
    return {
        "user": {
            "total_co2_saved_kg": round(total_saved, 1),
            "actions_count": len(user_actions),
            "estimated_annual_footprint_kg": estimated,
            "projected_annual_footprint_kg": round(projected, 0),
            "display_name": user.get("display_name", "User")
        },
        "global": global_stats
    }

@app.get("/api/stats/global")
async def get_global_stats():
    """Get real-time global stats"""
    # Calculate last minute stats
    one_minute_ago = datetime.now() - timedelta(minutes=1)
    recent_actions = [a for a in actions_db if datetime.fromisoformat(a["logged_at"]) > one_minute_ago]
    last_minute_kg = sum(a["co2_saved_kg"] for a in recent_actions)
    
    # Calculate today's stats
    today = datetime.now().date()
    today_actions = [a for a in actions_db if datetime.fromisoformat(a["logged_at"]).date() == today]
    today_kg = sum(a["co2_saved_kg"] for a in today_actions)
    
    return {
        "total_co2_saved_kg": round(global_stats["total_co2_saved_kg"], 1),
        "last_minute_kg": round(last_minute_kg, 2),
        "today_kg": round(today_kg, 1),
        "active_users": global_stats["total_users"],
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def root():
    # Serve the frontend HTML file
    frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")
    return FileResponse(frontend_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
