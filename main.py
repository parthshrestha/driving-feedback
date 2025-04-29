from dotenv import load_dotenv

from fastapi import FastAPI, Request, Form
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import timezone
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import os
from fastapi.responses import JSONResponse
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or use ["https://domain.com"] in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
load_dotenv()

# MongoDB Atlas connection URI (replace with your own URI securely later)
MONGO_URI = os.getenv("MONGO_URI")
if not MONGO_URI:
    raise ValueError("MONGO_URI not set. Please check your .env file or environment variables.")
client = AsyncIOMotorClient(MONGO_URI)
db = client.drivingFeedback        # DB name in mongo
collection = db.submissions        # Collection name

# In-memory session store
sessions = {}
# Global in-memory store for rate limiting
last_feedback_time = {}  # Format: { phone_number: datetime }
COOLDOWN_PERIOD = timedelta(minutes=120)  # cooldown period in minutes for rate limiting

@app.post("/sms", response_class=PlainTextResponse)
async def receive_sms(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...)
):
    user_number = From
    message = Body.strip().lower()

    session = sessions.get(user_number, {"step": 0, "attempts": 0})
    step = session["step"]
    now = datetime.now(timezone.utc)
    if step > 0:
        if user_number in last_feedback_time:
            elapsed = now - last_feedback_time[user_number]
            if elapsed < COOLDOWN_PERIOD:
                return "Please wait between feedback submissions." 

    if step == 0:# start of conversation
        if "1234" in message:
            session["step"] = 1
            session["attempts"] = 0
            sessions[user_number] = session
            return "Thanks! On a scale from 1 to 10, how was the driving?"
        else:
            return "To start, please text '1234'."

    elif step == 1:# get rating
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
        last_feedback_time[user_number] = datetime.now(timezone.utc)

        feedback_doc = {# mongo doc to store
            "phone": user_number,
            "rating": session.get("rating"),
            "comment": message,
            "timestamp": now
        }

        await collection.insert_one(feedback_doc)
        return "Thanks for the feedback!"

    else:
        return "You’ve already submitted feedback recently. Thanks again!"

@app.get("/rating", response_class=JSONResponse)
async def get_rating():
    # calculate average rating
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
    # Step 2: Get top 5 recent feedback comments
    feedback_cursor = collection.find(
        {"comment": {"$ne": None}}  # Only include documents with non-empty comment
    ).sort("timestamp", -1).limit(5)
    feedback_docs = await feedback_cursor.to_list(length=5)

    feedback_messages = [doc["comment"] for doc in feedback_docs if "comment" in doc]

    # Step 3: Return everything
    return {
        "average_rating": average_rating,
        "total_feedback": total_feedback,
        "feedback": feedback_messages
    }