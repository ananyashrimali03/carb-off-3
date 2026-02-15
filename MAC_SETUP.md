# CarbonBuddy - Mac Setup Guide

This project was originally developed on Windows. Here are the steps to get it running on your Mac.

## ✅ Setup Complete!

The project has been configured for Mac. Here's what was done:

1. ✅ Repository cloned to: `/Users/ashaykoradia/.gemini/antigravity/scratch/carb-off`
2. ✅ Virtual environment created (`venv/`)
3. ✅ Python dependencies installed
4. ✅ Start script updated for Mac compatibility

## 🚀 Quick Start

### Step 1: Get Your Dedalus API Key

This app uses **Dedalus API** (which routes to Anthropic Claude) instead of directly using Anthropic.

You'll need a Dedalus API key:
- Visit: https://dedaluslabs.ai (or check with the project owner for API access)
- Alternatively, you might need to modify the code to use Anthropic directly

### Step 2: Set Your API Key

```bash
export DEDALUS_API_KEY="your-key-here"
```

To make this persistent across terminal sessions, add it to your `~/.zshrc`:
```bash
echo 'export DEDALUS_API_KEY="your-key-here"' >> ~/.zshrc
source ~/.zshrc
```

### Step 3: Run the Application

From the project directory:
```bash
cd /Users/ashaykoradia/.gemini/antigravity/scratch/carb-off
./start.sh
```

This will:
- Activate the Python virtual environment
- Start the backend server on port 8000
- Start the frontend server on port 3000

### Step 4: Open in Browser

Navigate to: http://localhost:3000

## 🔧 Manual Setup (Alternative)

If you prefer to run the servers separately:

### Terminal 1 - Backend:
```bash
cd /Users/ashaykoradia/.gemini/antigravity/scratch/carb-off
source venv/bin/activate
cd backend
python3 main.py
```

### Terminal 2 - Frontend:
```bash
cd /Users/ashaykoradia/.gemini/antigravity/scratch/carb-off/frontend
python3 -m http.server 3000
```

## 📋 Project Structure

```
carb-off/
├── backend/                  # FastAPI backend
│   ├── main.py              # Main API server
│   ├── emission_factors.json # Carbon emission data
│   ├── requirements.txt     # Python dependencies
│   └── demo_data.json       # Sample data
├── frontend/                # Simple HTML/JS frontend
│   └── index.html           # Single-page app
├── venv/                    # Python virtual environment (Mac-specific)
├── start.sh                 # Startup script (updated for Mac)
├── README.md                # Project documentation
├── QUICKSTART.md            # Quick start guide
└── PROJECT_SUMMARY.md       # Project overview
```

## ⚠️ Important Notes for Mac

### Windows → Mac Differences Handled:

1. **Virtual Environment**: Mac requires using a virtual environment to install Python packages (due to PEP 668). This has been set up for you.

2. **Python Command**: Changed from `python` to `python3` in the start script.

3. **Path Handling**: Updated the start script to use proper path resolution that works on Mac.

4. **API Key**: The code expects `DEDALUS_API_KEY` (not `ANTHROPIC_API_KEY` as mentioned in some docs).

### If You Don't Have Dedalus API Access:

You can modify the code to use Anthropic Claude directly. Here's how:

1. Install the Anthropic SDK:
```bash
source venv/bin/activate
pip install anthropic
```

2. Update `backend/main.py` line 10 and 44-47 to use Anthropic's SDK instead of OpenAI client.

## 🐛 Troubleshooting

### "Module not found" errors
Make sure the virtual environment is activated:
```bash
source venv/bin/activate
```

### Port already in use
If ports 8000 or 3000 are already in use, kill the processes:
```bash
lsof -ti:8000 | xargs kill
lsof -ti:3000 | xargs kill
```

### Frontend can't connect to backend
- Check that the backend is running on port 8000
- Check the browser console for CORS errors
- Make sure both servers are running

## 📚 Additional Resources

- **Full Project Docs**: See `README.md`
- **Quick Start Guide**: See `QUICKSTART.md`
- **Project Summary**: See `PROJECT_SUMMARY.md`

## 🎯 Next Steps

1. Get a Dedalus API key (or modify code for direct Anthropic access)
2. Run `./start.sh` to start the application
3. Check out the demo script in `QUICKSTART.md` for presentation tips

---

**Need Help?**
- Check the project's original README for more details
- The app was built for Tartan Hacks 2025 hackathon
- It's an AI-powered climate action tracker using Claude for conversational AI
