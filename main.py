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


class Query(BaseModel):
    message: str

TAX_GAME_PROMPT = """
You are a tax planning game assistant. Based on the user's query, generate a personalized 10-month tax saving challenge with:

1. Monthly incomes that should not vary if the user gives the amount use that or else use 100000 for professionals and 1000 for students
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
        
        model = genai.GenerativeModel("gemini-2.5-pro")
        response = model.generate_content(full_prompt)
        
        print(f"📥 Gemini response length: {len(response.text) if response.text else 0}")
        print(f"📄 Response preview: {response.text[:1000] if response.text else 'No text'}...")
        
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

CHAT_CLASSIFICATION_PROMPT = """
You are a financial assistant that classifies user queries. Analyze the user's message and respond with ONLY a JSON object in this exact format:

{
  "category": "tax" | "investment" | "savings",
  "response": "A helpful response explaining the topic and offering assistance",
  "confidence": 0.8
}

Classification rules:
- "tax": Questions about tax saving, deductions, sections 80C/80D, tax planning, etc.
- "investment": Questions about stocks, mutual funds, SIP, returns, portfolio, etc.  
- "savings": Questions about budgeting, emergency funds, monthly savings goals, etc.

Always provide a helpful response and suggest playing the relevant game for hands-on learning.
"""

@app.post("/chat")
async def chat_with_bot(query: Query):
    full_prompt = f"User Query: {query.message}\n\n{CHAT_CLASSIFICATION_PROMPT}"
    
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return get_default_chat_response(query.message)
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(full_prompt)
        
        import json, re
        json_str = re.search(r"\{.*\}", response.text, re.DOTALL)
        if json_str:
            chat_data = json.loads(json_str.group(0))
            return chat_data
        else:
            return get_default_chat_response(query.message)
            
    except Exception as e:
        print(f"❌ Error in chat classification: {str(e)}")
        return get_default_chat_response(query.message)

SAVINGS_GAME_PROMPT = """
You are a savings planning game assistant. Based on the user's query, generate a personalized 10-month savings challenge with:

1. Monthly incomes that vary should not vary if the user gives the amount use that or else use 20000 for professionals and 1000 for students
2. Monthly savings options categorized as aggressive, moderate, and conservative
3. Each option should include: label, amount, emoji, category, and monthly savings goal

Please respond with ONLY a JSON object in this exact format:
{
  "monthlyIncomes": {
    "1": 80000, "2": 85000, "3": 90000, "4": 82000, "5": 88000,
    "6": 95000, "7": 87000, "8": 92000, "9": 89000, "10": 100000
  },
  "monthlyOptions": {
    "1": {
      "aggressive": [
        {"label": "High Savings Rate", "amount": 25000, "emoji": "🎯", "category": "Goal-based", "description": "Save 30% of income"}
      ],
      "moderate": [
        {"label": "Balanced Approach", "amount": 15000, "emoji": "⚖️", "category": "Balanced", "description": "Save 20% of income"}
      ],
      "conservative": [
        {"label": "Safe Savings", "amount": 8000, "emoji": "🛡️", "category": "Conservative", "description": "Save 10% of income"}
      ]
    }
  }
}

Make amounts realistic based on Indian salary levels and user context.
"""

# INVESTMENT_GAME_PROMPT = """
# You are an investment planning game assistant. Based on the user's query, generate a personalized 10-month investment challenge with:

# 1. Monthly investment budgets that doesnot vary if the user gives the amount use that or else use 2000 for students and 10000 for professionals
# 2. For each month, provide three investment options (safe, moderate, risky), and each option should **cost exactly the same as the monthly investment budget**.
#    - Do not split the budget across multiple options.
#    - Each option is a full investment of the entire monthly amount into a single asset.
#    - Ensure that all three options (safe, moderate, risky) have the **same investment amount** (equal to the monthly budget).
# 3. Each option should include: label, amount, emoji, returnRate, and risk level

# Please respond with ONLY a JSON object in this exact format:
# {
#   "monthlyBudgets": {
#     "1": 15000, "2": 12000, "3": 18000, "4": 14000, "5": 16000,
#     "6": 20000, "7": 13000, "8": 17000, "9": 15000, "10": 19000
#   },
#   "monthlyOptions": {
#     "1": {
#       "safe": [
#         {"label": "Fixed Deposit", "amount": 5000, "emoji": "🏦", "returnRate": 0.065, "risk": "low"}
#       ],
#       "moderate": [
#         {"label": "Balanced Funds", "amount": 8000, "emoji": "⚖️", "returnRate": 0.12, "risk": "medium"}
#       ],
#       "risky": [
#         {"label": "Small Cap Funds", "amount": 12000, "emoji": "🚀", "returnRate": 0.18, "risk": "high"}
#       ]
#     }
#   }
# }

# Make realistic investment amounts and returns based on Indian market conditions.
# the monthly investment should be exactly same as the monthly budget which the user provides.
# """
INVESTMENT_GAME_PROMPT = """
You are an investment planning game assistant. Based on the user's query, generate a personalized 10-month investment challenge.

Instructions:

1. Monthly Budget:
   - Use the same monthly investment budget for all 10 months.
   - If the user provides a value, use that exact amount.
   - If the user does not specify, use ₹2000 for students and ₹10000 for professionals.
   - Store this in a single key: "monthlyBudget" (not a dictionary).

2. Investment Options:
   - For each of the 10 months, generate three options: "safe", "moderate", and "risky".
   - Each option must invest the **full budget amount exactly** (no splitting or variation).
   - All three options per month must have the **same investment amount**, equal to "monthlyBudget".
   - Example: If monthlyBudget is 10000, each option's "amount" must be 10000.

3. Each option must include:
   - "label": name of the investment (e.g., Fixed Deposit, Balanced Fund)
   - "amount": must be exactly equal to "monthlyBudget"
   - "emoji": a relevant emoji for the option
   - "returnRate": decimal form (e.g., 0.06 means 6%)
   - "risk": "low", "medium", or "high"

Output Format (JSON only):
{
  "monthlyBudget": 10000,
  "monthlyOptions": {
    "1": {
      "safe": [
        {"label": "Fixed Deposit", "amount": 10000, "emoji": "🏦", "returnRate": 0.065, "risk": "low"}
      ],
      "moderate": [
        {"label": "Balanced Fund", "amount": 10000, "emoji": "⚖️", "returnRate": 0.12, "risk": "medium"}
      ],
      "risky": [
        {"label": "Small Cap Fund", "amount": 10000, "emoji": "🚀", "returnRate": 0.18, "risk": "high"}
      ]
    },
    "2": { ... },
    ...
    "10": { ... }
  }
}

Strict Rules:
- Absolutely no variations in the amount field across options or months.
- Do not use a dictionary of varying monthly budgets. Only one fixed value in "monthlyBudget".
- Do not abbreviate or add explanations outside the JSON.
- The value in "amount" in every option must match exactly with "monthlyBudget".
"""




# @app.post("/generate-savings-game")
# async def generate_savings_game(query: Query):
#     full_prompt = f"User Query: {query.message}\n\n{SAVINGS_GAME_PROMPT}"
#     print(f"🔍 Processing savings query: {query.message}")
    
#     try:
#         # GEMINI API CALL
#         api_key = os.getenv("GEMINI_API_KEY")
#         print(f"🔑 API Key status: {'Found' if api_key else 'Not found'}")
        
#         if not api_key:
#             print("⚠️  No API key found - using default savings data")
#             return get_default_savings_game_data()
            
#         print("🚀 Calling Gemini API for savings game...")
#         genai.configure(api_key=api_key)
        
#         model = genai.GenerativeModel("gemini-1.5-flash")
#         response = model.generate_content(full_prompt)
        
#         print(f"📥 Gemini response length: {len(response.text) if response.text else 0}")
#         print(f"📄 Response preview: {response.text[:200] if response.text else 'No text'}...")
        
#         # Parse JSON string from Gemini response safely
#         import json, re
#         json_str = re.search(r"\{.*\}", response.text, re.DOTALL)
#         if json_str:
#             print("✅ JSON found in response, parsing...")
#             game_data = json.loads(json_str.group(0))
#             print("🎯 Successfully generated custom savings game data!")
#             return game_data
#         else:
#             print("⚠️  No JSON found in response - using default savings data")
#             return get_default_savings_game_data()
            
#     except Exception as e:
#         print(f"❌ Error generating savings game: {str(e)}")
#         return get_default_savings_game_data()

@app.post("/generate-savings-game")
async def generate_savings_game(query: Query):
    full_prompt = f"User Query: {query.message}\n\n{SAVINGS_GAME_PROMPT}"
    print(f"🔍 Processing savings query: {query.message}")

    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("⚠️ No API key found - using default savings data")
            return get_default_savings_data()

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(full_prompt)

        import json, re
        json_str = re.search(r"\{.*\}", response.text, re.DOTALL)
        if json_str:
            game_data = json.loads(json_str.group(0))
            print("🎯 Custom savings game generated!")
            return game_data
        else:
            print("⚠️ No JSON found - using default")
            return get_default_savings_data()

    except Exception as e:
        print(f"❌ Error: {e}")
        return get_default_savings_data()

def get_default_savings_data():
    return {
        "monthlyIncomes": {
            "1": 5000, "2": 6000, "3": 5500, "4": 5800, "5": 6200,
            "6": 5900, "7": 6100, "8": 6300, "9": 6000, "10": 6500
        },
        "monthlyOptions": {
            "1": {
                "aggressive": [{"label": "High Savings", "amount": 2500, "emoji": "💸", "category": "Goal-based", "description": "Save 50%"}],
                "moderate": [{"label": "Balanced", "amount": 1500, "emoji": "⚖️", "category": "Balanced", "description": "Save 30%"}],
                "conservative": [{"label": "Safe", "amount": 800, "emoji": "🛡️", "category": "Safe", "description": "Save 15%"}]
            }
        }
    }

    



@app.post("/generate-investment-game")
async def generate_investment_game(query: Query):
    full_prompt = f"User Query: {query.message}\n\n{INVESTMENT_GAME_PROMPT}"
    print(f"🔍 Processing investment query: {query.message}")
    
    try:
        # GEMINI API CALL
        api_key = os.getenv("GEMINI_API_KEY")
        print(f"🔑 API Key status: {'Found' if api_key else 'Not found'}")
        
        if not api_key:
            print("⚠️  No API key found - using default investment data")
            return get_default_investment_game_data()
            
        print("🚀 Calling Gemini API for investment game...")
        genai.configure(api_key=api_key)
        
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
            print("🎯 Successfully generated custom investment game data!")
            return game_data
        else:
            print("⚠️  No JSON found in response - using default investment data")
            return get_default_investment_game_data()
            
    except Exception as e:
        print(f"❌ Error generating investment game: {str(e)}")
        return get_default_investment_game_data()

def get_default_savings_game_data():
    base_options = {
        "aggressive": [
            {"label": "High Savings Rate", "amount": 25000, "emoji": "🎯", "category": "Goal-based", "description": "Save 30% of income"},
            {"label": "Emergency Fund Boost", "amount": 20000, "emoji": "🚨", "category": "Emergency", "description": "Build 6-month expenses"},
            {"label": "Investment Surplus", "amount": 18000, "emoji": "📈", "category": "Investment", "description": "Extra for investments"}
        ],
        "moderate": [
            {"label": "Balanced Approach", "amount": 15000, "emoji": "⚖️", "category": "Balanced", "description": "Save 20% of income"},
            {"label": "Goal-based Savings", "amount": 12000, "emoji": "🎯", "category": "Goals", "description": "For specific targets"},
            {"label": "Systematic Savings", "amount": 10000, "emoji": "📊", "category": "Systematic", "description": "Regular monthly amount"}
        ],
        "conservative": [
            {"label": "Safe Savings", "amount": 8000, "emoji": "🛡️", "category": "Conservative", "description": "Save 10% of income"},
            {"label": "Basic Emergency Fund", "amount": 6000, "emoji": "💰", "category": "Emergency", "description": "Start emergency fund"},
            {"label": "Small Steps", "amount": 4000, "emoji": "👣", "category": "Beginner", "description": "Begin savings habit"}
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

def get_default_investment_game_data():
    base_options = {
        "safe": [
            {"label": "Fixed Deposit", "amount": 5000, "emoji": "🏦", "returnRate": 0.065, "risk": "low"},
            {"label": "PPF", "amount": 7000, "emoji": "🛡️", "returnRate": 0.075, "risk": "low"},
            {"label": "NSC", "amount": 6000, "emoji": "📜", "returnRate": 0.068, "risk": "low"}
        ],
        "moderate": [
            {"label": "Balanced Funds", "amount": 8000, "emoji": "⚖️", "returnRate": 0.12, "risk": "medium"},
            {"label": "Hybrid Funds", "amount": 10000, "emoji": "🔄", "returnRate": 0.11, "risk": "medium"},
            {"label": "Debt Funds", "amount": 7000, "emoji": "📋", "returnRate": 0.08, "risk": "medium"}
        ],
        "risky": [
            {"label": "Small Cap Funds", "amount": 12000, "emoji": "🚀", "returnRate": 0.18, "risk": "high"},
            {"label": "Equity Funds", "amount": 15000, "emoji": "📈", "returnRate": 0.15, "risk": "high"},
            {"label": "Sector Funds", "amount": 10000, "emoji": "🏭", "returnRate": 0.20, "risk": "high"}
        ]
    }
    
    monthly_options = {}
    for i in range(1, 11):
        monthly_options[str(i)] = base_options.copy()
    
    return {
        "monthlyBudgets": {
            "1": 15000, "2": 12000, "3": 18000, "4": 14000, "5": 16000,
            "6": 20000, "7": 13000, "8": 17000, "9": 15000, "10": 19000
        },
        "monthlyOptions": monthly_options
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

def get_default_chat_response(message):
    # Simple keyword-based classification as fallback
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["tax", "deduction", "80c", "80d", "section"]):
        return {
            "category": "tax",
            "response": "I can help you with tax planning! Tax saving is important for building wealth. I can suggest various tax-saving instruments like ELSS, PPF, insurance, and more based on your income and goals.",
            "confidence": 0.7
        }
    elif any(word in message_lower for word in ["invest", "stock", "mutual fund", "sip", "portfolio", "returns"]):
        return {
            "category": "investment", 
            "response": "Investment planning is key to wealth creation! I can guide you through different investment options like mutual funds, stocks, bonds, and help you understand risk-return profiles.",
            "confidence": 0.7
        }
    elif any(word in message_lower for word in ["save", "budget", "emergency", "goal", "money"]):
        return {
            "category": "savings",
            "response": "Smart savings habits are the foundation of financial health! I can help you create budgets, set savings goals, and develop strategies to build your emergency fund.",
            "confidence": 0.7
        }
    else:
        return {
            "category": "savings",
            "response": "I'm your financial assistant! I can help with tax planning, investment strategies, and savings goals. What specific area would you like to explore?",
            "confidence": 0.5
        }

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