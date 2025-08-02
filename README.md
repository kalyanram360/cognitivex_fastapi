# Finance chatbot with game based application

## Setup Instructions

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**

   - Copy `.env.example` to `.env`
   - Get a Gemini API key from Google AI Studio
   - Add your API key to the `.env` file:
     ```
     GEMINI_API_KEY=your_actual_api_key_here
     ```

3. **Run the Application**

   ```bash
   uvicorn main:app --reload
   ```

4. **Access the Tax Game**
   - Open your browser and go to: `http://localhost:8000/tax-game`
   - Enter your tax planning requirements in the text area
   - Click "Generate My Tax Game" for AI-customized options
   - Or click "Start with Default Settings" for a quick start

## Features

- **AI-Powered Customization**: Uses Gemini AI to generate personalized tax saving options based on user input
- **Dynamic Game Content**: Monthly incomes and tax saving options are generated based on user's financial profile
- **Fallback System**: If AI generation fails, the game uses sensible default options
- **Interactive Gameplay**: 10-month tax planning challenge with realistic Indian tax scenarios
- **Multiple Tax Sections**: Covers various sections like 80C, 80D, 80E, NPS, etc.

## API Endpoints

- `GET /tax-game` - Serves the tax game HTML page
- `POST /generate-tax-game` - Generates custom game data using Gemini AI

## Example User Prompts

- "I'm a software engineer earning 15 LPA, want to maximize tax savings while building wealth"
- "Senior citizen with 8 LPA pension, focus on health insurance and safe investments"
- "Young professional, 12 LPA salary, planning to buy a house in 2 years"
