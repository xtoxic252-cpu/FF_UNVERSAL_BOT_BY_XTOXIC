import os
import threading
import time
import random
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# --- FIXED: Isse Website aur Railway ke beech ka connection nahi tootega ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

class BotRequest(BaseModel):
    uid: str = "0"
    team_code: str = "0"

# --- BOT LOGIC (Independent Threads) ---

def run_glory_bot(uid):
    print(f"[SHIELD] Glory Bot Active for: {uid}")
    while True:
        time.sleep(random.randint(30, 60))

def run_remote_bot(uid):
    print(f"[TROLL] Remote Bot Spamming on: {uid}")
    while True:
        time.sleep(0.5)

def run_dress_bot(team_code):
    print(f"[DRESS] Injecting Sakura/V-Badge in Code: {team_code}")
    while True:
        time.sleep(100)

# --- API ENDPOINTS ---

@app.get("/")
def health_check():
    return {"status": "乂 T O X I C ╰︿╯ Live"}

@app.post("/execute/{bot_type}")
async def start_bot(bot_type: str, data: BotRequest, bg: BackgroundTasks):
    if bot_type == "glory":
        bg.add_task(run_glory_bot, data.uid)
    elif bot_type == "remote":
        bg.add_task(run_remote_bot, data.uid)
    elif bot_type == "dress":
        bg.add_task(run_dress_bot, data.team_code)
    return {"message": f"{bot_type} bot deployed successfully!"}

# --- FIXED: Railway Port Binding ---
if __name__ == "__main__":
    import uvicorn
    # Railway environment se port uthata hai, default 8000
    port = int(os.environ.get("PORT", 8000))
    # '0.0.0.0' hona zaroori hai Railway ke liye
    uvicorn.run(app, host="0.0.0.0", port=port)
