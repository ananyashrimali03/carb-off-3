"""
Seed the database with realistic demo data to make the collective counter impressive
This simulates 20 CMU students over 2 weeks
"""
import sys
sys.path.append('/home/claude/carbonbuddy/backend')

from datetime import datetime, timedelta
import random
import json

# Student profiles (realistic CMU archetypes)
STUDENTS = [
    {"name": "Sarah", "college": "CFA", "commute": "walk", "diet": "vegetarian", "distance_km": 0},
    {"name": "Mike", "college": "SCS", "commute": "car", "diet": "meat_mixed", "distance_km": 12},
    {"name": "Priya", "college": "Tepper", "commute": "bus", "diet": "vegan", "distance_km": 8},
    {"name": "Jake", "college": "Engineering", "commute": "bike", "diet": "meat_mixed", "distance_km": 5},
    {"name": "Emma", "college": "Dietrich", "commute": "bus", "diet": "vegetarian", "distance_km": 10},
    {"name": "David", "college": "SCS", "commute": "car", "diet": "beef_heavy", "distance_km": 15},
    {"name": "Lisa", "college": "CFA", "commute": "walk", "diet": "vegan", "distance_km": 0},
    {"name": "Alex", "college": "Tepper", "commute": "train", "diet": "fish", "distance_km": 20},
    {"name": "Maria", "college": "Engineering", "commute": "bike", "diet": "vegetarian", "distance_km": 4},
    {"name": "Tom", "college": "SCS", "commute": "bus", "diet": "meat_mixed", "distance_km": 7},
    {"name": "Nina", "college": "Dietrich", "commute": "walk", "diet": "vegetarian", "distance_km": 0},
    {"name": "Chris", "college": "Engineering", "commute": "car", "diet": "meat_mixed", "distance_km": 14},
    {"name": "Amy", "college": "CFA", "commute": "bike", "diet": "vegan", "distance_km": 6},
    {"name": "Ryan", "college": "Tepper", "commute": "bus", "diet": "beef_heavy", "distance_km": 9},
    {"name": "Sophia", "college": "SCS", "commute": "walk", "diet": "fish", "distance_km": 0},
    {"name": "Dan", "college": "Engineering", "commute": "car", "diet": "meat_mixed", "distance_km": 11},
    {"name": "Rachel", "college": "Dietrich", "commute": "train", "diet": "vegetarian", "distance_km": 18},
    {"name": "Kevin", "college": "SCS", "commute": "bike", "diet": "vegan", "distance_km": 5},
    {"name": "Laura", "college": "CFA", "commute": "bus", "diet": "vegetarian", "distance_km": 8},
    {"name": "Ben", "college": "Tepper", "commute": "car", "diet": "meat_mixed", "distance_km": 13},
]

# Load emission factors
with open('/home/claude/carbonbuddy/backend/emission_factors.json', 'r') as f:
    emission_data = json.load(f)
    EMISSION_FACTORS = {f['action_type']: f for f in emission_data['factors']}

def generate_actions_for_student(student, days=14):
    """Generate realistic actions for a student over N days"""
    actions = []
    
    # Map diet types
    diet_map = {
        "vegetarian": "vegetarian_meal",
        "vegan": "vegan_meal",
        "meat_mixed": "meat_mixed_meal",
        "beef_heavy": "beef_heavy_meal",
        "fish": "fish_meal"
    }
    
    # Map commute types
    commute_map = {
        "walk": "bike_walk",
        "bike": "bike_walk",
        "bus": "bus",
        "train": "train_electric",
        "car": "car_petrol"
    }
    
    for day in range(days):
        date = datetime.now() - timedelta(days=days-day-1)
        
        # Commute actions (5 days/week)
        if day % 7 < 5 and student["distance_km"] > 0:  # Weekdays only
            # Baseline is car, actual is their mode
            commute_type = commute_map[student["commute"]]
            if commute_type != "car_petrol":  # Only log if not driving
                baseline = EMISSION_FACTORS["car_petrol"]["emission_factor_kg_co2e"] * student["distance_km"] * 2
                actual = EMISSION_FACTORS[commute_type]["emission_factor_kg_co2e"] * student["distance_km"] * 2
                saved = baseline - actual
                
                actions.append({
                    "logged_at": date.isoformat(),
                    "category": "transport",
                    "action_type": commute_type,
                    "quantity": student["distance_km"] * 2,
                    "co2_saved_kg": saved
                })
        
        # Food actions (random, but matching their diet)
        # 60% chance they log a meal each day
        if random.random() < 0.6:
            meal_type = diet_map[student["diet"]]
            # Baseline is meat_mixed
            baseline = EMISSION_FACTORS["meat_mixed_meal"]["emission_factor_kg_co2e"]
            actual = EMISSION_FACTORS[meal_type]["emission_factor_kg_co2e"]
            saved = max(0, baseline - actual)
            
            if saved > 0:  # Only log if they saved something
                actions.append({
                    "logged_at": date.isoformat(),
                    "category": "food",
                    "action_type": meal_type,
                    "quantity": 1,
                    "co2_saved_kg": saved
                })
        
        # Occasional lifestyle actions (20% chance per day)
        if random.random() < 0.2:
            lifestyle_actions = [
                ("reusable_bottle", 0.08),
                ("reusable_bag", 0.03),
                ("no_food_waste", 0.9),
                ("local_produce", 0.3),
            ]
            action = random.choice(lifestyle_actions)
            actions.append({
                "logged_at": date.isoformat(),
                "category": "lifestyle",
                "action_type": action[0],
                "quantity": 1,
                "co2_saved_kg": action[1]
            })
    
    return actions

# Generate all actions
print("Generating realistic demo data for 20 CMU students over 2 weeks...")
all_actions = []
total_saved = 0

for student in STUDENTS:
    actions = generate_actions_for_student(student, days=14)
    all_actions.extend(actions)
    student_total = sum(a["co2_saved_kg"] for a in actions)
    total_saved += student_total
    print(f"{student['name']} ({student['college']}): {len(actions)} actions, {student_total:.1f} kg saved")

print(f"\nTotal: {len(all_actions)} actions, {total_saved:.1f} kg CO2 saved")
print(f"Average per student: {total_saved/20:.1f} kg")

# Save to JSON
output = {
    "students": STUDENTS,
    "actions": all_actions,
    "summary": {
        "total_actions": len(all_actions),
        "total_co2_saved_kg": round(total_saved, 1),
        "num_students": len(STUDENTS),
        "period_days": 14,
        "generated_at": datetime.now().isoformat()
    }
}

with open('/home/claude/carbonbuddy/backend/demo_data.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n✅ Demo data saved to demo_data.json")
print(f"   Use this data to seed your database for an impressive demo!")
