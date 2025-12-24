# TubeTale Analytics

**AI-Powered YouTube Intelligence Platform**

A narrative-driven analytics tool that provides deep insights into YouTube channels and videos using Google Gemini AI.

## Features

- **Solo Audit** - Analyze any YouTube channel's growth, content strategy, and audience sentiment
- **Battle Arena** - Compare 2-5 channels head-to-head with detailed scoring
- **Truth Auditor** - Fact-check claims in YouTube videos with AI verification

## Clone & Setup

```bash
# Clone the repository
git clone https://github.com/9mit/Youtube_Intelligence.git
cd Youtube_Intelligence

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Create .env file with your API key
echo GEMINI_API_KEY=your_api_key_here > .env
echo FLASK_SECRET_KEY=any_random_string_here >> .env

# Run the application
python app.py
```

Visit `http://localhost:5000` to use the app.

---

