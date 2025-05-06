from dotenv import load_dotenv
from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import timezone, datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://nayadriver.com","https://nayadriver.com", "http://localhost:3000"],  # restrict to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not set. Please check your .env file or environment variables.")

client = AsyncIOMotorClient(MONGO_URI)
db = client.drivingFeedback
collection = db.submissions
blocked_collection = db.blocked_numbers  # New collection for blocked users

sessions = {}
last_feedback_time = {}
COOLDOWN_PERIOD = timedelta(minutes=120)

@app.post("/sms", response_class=PlainTextResponse)
async def receive_sms(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...)
):
    user_number = From
    message = Body.strip().lower()
    now = datetime.now(timezone.utc)

    # Silent block: don't respond to already submitted numbers
    if await blocked_collection.find_one({"phone": user_number}):
        print(f"Blocked user {user_number} tried to message again.")
        return PlainTextResponse(content="", status_code=200)

    session = sessions.get(user_number, {"step": 0, "attempts": 0})
    step = session["step"]

    if step == 0:
        if "1234" in message:
            session["step"] = 1
            session["attempts"] = 0
            sessions[user_number] = session
            return "Thanks! On a scale from 1 to 10, how was the driving?"
        else:
            return "To start, please text '1234'."

    elif step == 1:
        try:
            rating = int(message)
            if 1 <= rating <= 10:
                session["rating"] = rating
                session["step"] = 2
                sessions[user_number] = session
                return "Got it. Want to share what happened?"
            else:
                raise ValueError()
        except ValueError:
            session["attempts"] += 1
            if session["attempts"] >= 2:
                session["step"] = 2
                sessions[user_number] = session
                return "Got it. Want to share what happened?"
            else:
                sessions[user_number] = session
                return "Please send a number between 1 and 10."

    elif step == 2:
        session["message"] = message
        session["step"] = 3
        sessions[user_number] = session

        feedback_doc = {
            "phone": user_number,
            "rating": session.get("rating"),
            "comment": message,
            "timestamp": now
        }

        await collection.insert_one(feedback_doc)
        await blocked_collection.insert_one({"phone": user_number})
        return "Thanks for the feedback!"

    else:
        # fallback — shouldn't happen due to block logic
        return PlainTextResponse(content="", status_code=200)

@app.get("/rating", response_class=JSONResponse)
async def get_rating():
    pipeline = [
        {"$group": {"_id": None, "average": {"$avg": "$rating"}, "count": {"$sum": 1}}}
    ]
    agg_result = await collection.aggregate(pipeline).to_list(length=1)

    if not agg_result:
        average_rating = 0
        total_feedback = 0
    else:
        result = agg_result[0]
        average_rating = round(result["average"], 2)
        total_feedback = result["count"]

    feedback_cursor = collection.find({"comment": {"$ne": None}}).sort("timestamp", -1).limit(10)
    feedback_docs = await feedback_cursor.to_list(length=10)

    feedback_messages = [
        {
            "rating": doc.get("rating", 0),
            "comment": doc.get("comment", "")
        }
        for doc in feedback_docs if "comment" in doc
    ]

    return {
        "average_rating": average_rating,
        "total_feedback": total_feedback,
        "feedback": feedback_messages
    }
