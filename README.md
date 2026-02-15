# Deployed APP Link
https://carb-off-3.onrender.com/

# Carb-off Backend

A FastAPI backend for CarbonBuddy that powers AI-driven climate action tracking through conversational interfaces and smart carbon calculations.

## What This Does

The backend provides three main services:

1. **Onboarding Baseline Calculation** - Takes user lifestyle data (commute, diet, energy usage) and calculates their annual carbon footprint
2. **Daily Task Generation** - Creates personalized daily action items based on user profile and calculates CO2 savings
3. **Conversational Action Logging** - Uses Claude AI to extract climate actions from natural language and calculate carbon impact against personal baselines

## Tech Stack

- **FastAPI** - Modern Python web framework
- **Anthropic Claude** - AI for natural language understanding (via Dedalus API)
- **Python 3.8+** - Backend runtime

## Project Structure

```
backend/
├── main.py                    # FastAPI server with all endpoints
├── emission_factors.json      # Carbon emission data by activity type
├── requirements.txt           # Python dependencies
└── demo_data.json            # Sample user/task data for testing
```

## Running Locally

### Prerequisites

You need a Dedalus API key (which routes to Anthropic Claude). Get one from your hackathon organizers or sign up at dedaluslabs.ai.

### Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (Mac/Linux)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
export DEDALUS_API_KEY="your-key-here"

# Run the server
python3 main.py
```

The backend will start on **http://localhost:8000**

### Making It Persistent

Add your API key to `~/.zshrc` (Mac) or `~/.bashrc` (Linux):

```bash
echo 'export DEDALUS_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

## API Endpoints

### `POST /api/onboard-quick`
Calculates baseline carbon footprint from lifestyle survey.

**Request:**
```json
{
  "city": "Pittsburgh",
  "country": "USA",
  "commute_mode": "car_petrol",
  "commute_distance": 15,
  "diet": "meat_lover",
  "has_ac": true,
  "has_heating": true
}
```

**Response:**
```json
{
  "baseline_co2_annual": 8234.5,
  "weekly_baseline": 158.4,
  "breakdown": {
    "transport": 1170.0,
    "food": 2500.0,
    "energy": 2000.0,
    "other": 2564.5
  }
}
```

### `POST /api/chat`
Natural language action logging with AI extraction.

**Request:**
```json
{
  "message": "I biked 25 km to campus today",
  "user": {
    "commute_mode": "car_petrol",
    "diet": "meat_lover"
  }
}
```

**Response:**
```json
{
  "response_text": "Amazing! You saved 5.2 kg of CO2...",
  "total_saved_today": 5.25,
  "actions_logged": [
    {
      "category": "transport",
      "action_type": "bike_walk",
      "quantity": 25,
      "co2_saved": 5.25
    }
  ]
}
```

### `GET /api/health`
Health check endpoint.

## How Frontend Calls Backend

The single-page React app (`frontend/index.html`) makes fetch calls:

```javascript
// Example: Chat logging
const response = await fetch('http://localhost:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: userInput,
    user: userProfile  // from localStorage
  })
});

const data = await response.json();
// Updates UI with CO2 savings and leaderboard
```

CORS is enabled for `http://localhost:3000` in development.

## Secrets Management

**Development:**
- API key stored in environment variable `DEDALUS_API_KEY`
- Never committed to git (see `.gitignore`)

**Production (if deploying):**
- Use platform-specific secret management:
  - Vercel: Environment Variables in dashboard
  - Railway: Secret Variables
  - Heroku: Config Vars

**Security Note:** The current implementation uses Dedalus API (OpenAI-compatible endpoint) pointing to Claude. For direct Anthropic usage, install `anthropic` package and modify the client initialization in `main.py`.

## Carbon Calculation Logic

### How It Works

1. **User describes action** - "I took the bus 10km"
2. **Claude extracts details** - category: transport, action: transit, quantity: 10km
3. **Backend compares to baseline** - User's normal commute is car (0.21 kg/km)
4. **Calculates savings** - (0.21 - 0.05) × 10 = 1.6 kg CO2 saved

### Emission Factors

Located in `emission_factors.json`:

```json
{
  "transport": {
    "car_petrol": 0.21,
    "bus": 0.05,
    "bike_walk": 0.0
  },
  "food": {
    "meat_lover": 3.7,
    "vegan": 1.0
  }
}
```

These are approximations based on EPA and IPCC data, adjusted for hackathon scope.

## Troubleshooting

**"Module not found" errors**
```bash
# Make sure venv is activated
source venv/bin/activate
pip install -r requirements.txt
```

**"API key not found"**
```bash
# Check environment variable is set
echo $DEDALUS_API_KEY
```

**CORS errors in browser**
- Backend must run on port 8000
- Frontend must run on port 3000
- Check browser console for specific error

**Port already in use**
```bash
# Kill existing process on port 8000
lsof -ti:8000 | xargs kill
```

## Development Notes

- Built for Tartan Hacks 2025 hackathon
- Designed to work with single-page frontend (no database required for MVP)
- AI responses tuned for friendly, motivating tone
- All calculations done server-side for accuracy

## Future Improvements

- [ ] Add PostgreSQL for persistent user data
- [ ] Implement proper authentication/sessions
- [ ] Add more granular emission factors by region
- [ ] Support multiple AI providers beyond Claude
- [ ] Add admin dashboard for monitoring usage
- [ ] Rate limiting on chat endpoint

---

**Questions?** Check `CHAT_LOGGING_GUIDE.md` for detailed flow explanations or `MAC_SETUP.md` for platform-specific setup help.
