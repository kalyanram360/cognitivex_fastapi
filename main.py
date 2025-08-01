from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from routes import chat  # Assuming chat.py inside routes/
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import google.generativeai as genai 
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI()

# Mount templates directory
templates = Jinja2Templates(directory="templates")

# Include your route
app.include_router(chat.router)


EXTRA_PROMPT = """
You are a personal finance game assistant...
(<< use the long prompt from above >>)
"""

class Query(BaseModel):
    message: str

@app.post("/generate-savings-game")
async def generate_game(query: Query):
    full_prompt = f"User Query: {query.message}\n\n{EXTRA_PROMPT}"
    
    # GEMINI API CALL (example with SDK)
    genai.configure(api_key="YOUR_GEMINI_API_KEY")
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(full_prompt)
    
    # Parse JSON string from Gemini response safely
    import json, re
    # json_str = re.search(r"\{.*\}", response.text, re.DOTALL).group(0)
    json_str = re.search(r"\{.*\}", response.parts[0].text, re.DOTALL)

    game_data = json.loads(json_str)
    print(f"Game Data: {game_data}")  # Debugging line
    return game_data

TAX_GAME_PROMPT = """
You are a tax planning game assistant. Based on the user's query, generate a personalized 10-month tax saving challenge with:

1. Monthly incomes that vary realistically (should be reasonable amounts based on user's context)
2. Monthly tax saving options categorized as high, medium, and low saving potential
3. Each option should include: label, amount, emoji, tax section, and calculated tax saving (30% tax rate)

Please respond with ONLY a JSON object in this exact format:
{
  "monthlyIncomes": {
    "1": 80000, "2": 85000, "3": 90000, "4": 82000, "5": 88000,
    "6": 95000, "7": 87000, "8": 92000, "9": 89000, "10": 100000
  },
  "monthlyOptions": {
    "1": {
      "high": [
        {"label": "ELSS Mutual Funds", "amount": 50000, "emoji": "📈", "section": "80C", "taxSaving": 15000}
      ],
      "medium": [
        {"label": "NSC Investment", "amount": 30000, "emoji": "📜", "section": "80C", "taxSaving": 9000}
      ],
      "low": [
        {"label": "EPF Contribution", "amount": 12000, "emoji": "👔", "section": "80C", "taxSaving": 3600}
      ]
    }
  }
}

Make sure:
- All amounts are realistic Indian tax saving options
- Tax savings are calculated at 30% of investment amount
- Include variety of sections like 80C, 80D, 80E, etc.
- Use appropriate emojis for each investment type
- Provide 3 options each for high/medium/low categories per month
- Total 10 months of data
"""

@app.post("/generate-tax-game")
async def generate_tax_game(query: Query):
    
    full_prompt = f"User Query: {query.message}\n\n{TAX_GAME_PROMPT}"
    print(f"🔍 Processing user query: {query.message}")
    
    try:
        # GEMINI API CALL
        api_key = os.getenv("GEMINI_API_KEY")
        print(f"🔑 API Key status: {'Found' if api_key else 'Not found'}")
        
        if not api_key:
            print("⚠️  No API key found - using default data")
            return get_default_tax_game_data()
            
        print("🚀 Calling Gemini API...")
        genai.configure(api_key=api_key)
        
        # List available models for debugging
        try:
            models = genai.list_models()
            print("Available models:")
            for model in models:
                if 'generateContent' in model.supported_generation_methods:
                    print(f"  - {model.name}")
        except Exception as e:
            print(f"Could not list models: {e}")
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(full_prompt)
        
        print(f"📥 Gemini response length: {len(response.text) if response.text else 0}")
        print(f"📄 Response preview: {response.text[:200] if response.text else 'No text'}...")
        
        # Parse JSON string from Gemini response safely
        import json, re
        json_str = re.search(r"\{.*\}", response.text, re.DOTALL)
        if json_str:
            print("✅ JSON found in response, parsing...")
            game_data = json.loads(json_str.group(0))
            print("🎯 Successfully generated custom game data!")
            return game_data
        else:
            print("⚠️  No JSON found in response - using default data")
            return get_default_tax_game_data()
            
    except Exception as e:
        print(f"❌ Error calling Gemini API: {str(e)}")
        # Return default data if API call fails
        return get_default_tax_game_data()

def get_default_tax_game_data():
    base_options = {
        "high": [
            {"label": "ELSS Mutual Funds", "amount": 50000, "emoji": "📈", "section": "80C", "taxSaving": 15000},
            {"label": "PPF Investment", "amount": 150000, "emoji": "🛡️", "section": "80C", "taxSaving": 45000},
            {"label": "Life Insurance Premium", "amount": 100000, "emoji": "🏥", "section": "80C", "taxSaving": 30000}
        ],
        "medium": [
            {"label": "NSC Investment", "amount": 30000, "emoji": "📜", "section": "80C", "taxSaving": 9000},
            {"label": "ULIP Premium", "amount": 25000, "emoji": "🔗", "section": "80C", "taxSaving": 7500},
            {"label": "Tax Saver FD", "amount": 20000, "emoji": "🏦", "section": "80C", "taxSaving": 6000}
        ],
        "low": [
            {"label": "EPF Contribution", "amount": 12000, "emoji": "👔", "section": "80C", "taxSaving": 3600},
            {"label": "Home Loan Principal", "amount": 15000, "emoji": "🏠", "section": "80C", "taxSaving": 4500},
            {"label": "Sukanya Samriddhi", "amount": 10000, "emoji": "👧", "section": "80C", "taxSaving": 3000}
        ]
    }
    
    monthly_options = {}
    for i in range(1, 11):
        monthly_options[str(i)] = base_options.copy()
    
    return {
        "monthlyIncomes": {
            "1": 80000, "2": 85000, "3": 90000, "4": 82000, "5": 88000,
            "6": 95000, "7": 87000, "8": 92000, "9": 89000, "10": 100000
        },
        "monthlyOptions": monthly_options
    }