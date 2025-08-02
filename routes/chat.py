from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/chat")
async def load_chat(request: Request):
    return templates.TemplateResponse("chat.html", {"request": request})

@router.get("/tax-game")
async def load_tax_game(request: Request):
    return templates.TemplateResponse("taxte_game.html", {"request": request})

@router.get("/savings-game")
async def load_savings_game(request: Request):
    return templates.TemplateResponse("savings_game_new.html", {"request": request})

@router.get("/investment-game")
async def load_investment_game(request: Request):
    return templates.TemplateResponse("investment_game.html", {"request": request})
