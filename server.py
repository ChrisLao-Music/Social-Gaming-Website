from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime, timezone
import base64
import uuid

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

app = FastAPI()
api_router = APIRouter(prefix="/api")

# Pydantic Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    username: str
    handle: str
    avatar: str
    bio: str
    followers: int = 0
    following: int = 0
    isOnline: bool = True

class Comment(BaseModel):
    id: int
    author: str
    text: str
    timestamp: str = "Just now"

class Post(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    userId: int
    username: str
    handle: str
    avatar: str
    content: str
    image: Optional[str] = None
    likes: int = 0
    comments: List[Comment] = []
    shares: int = 0
    timestamp: str
    gameTag: str
    liked: bool = False

class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: int
    type: str
    user: str
    avatar: str
    text: str
    time: str

class CreatePostRequest(BaseModel):
    caption: str
    gameTag: str
    image: Optional[str] = None

class LikeRequest(BaseModel):
    liked: bool

class CommentRequest(BaseModel):
    text: str

# API Routes
@api_router.get("/")
async def root():
    return {"message": "GameHub Social API"}

@api_router.get("/posts", response_model=List[Post])
async def get_posts():
    posts = await db.posts.find({}, {"_id": 0}).to_list(1000)
    return sorted(posts, key=lambda x: x['id'], reverse=True)

@api_router.get("/posts/{post_id}", response_model=Post)
async def get_post(post_id: int):
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@api_router.post("/posts", response_model=Post)
async def create_post(post_data: CreatePostRequest):
    posts = await db.posts.find({}, {"_id": 0}).to_list(1000)
    new_id = max([p['id'] for p in posts], default=0) + 1
    
    current_user = await db.users.find_one({"id": 1}, {"_id": 0})
    
    new_post = {
        "id": new_id,
        "userId": 1,
        "username": current_user['username'],
        "handle": current_user['handle'],
        "avatar": current_user['avatar'],
        "content": post_data.caption,
        "image": post_data.image,
        "likes": 0,
        "comments": [],
        "shares": 0,
        "timestamp": "Just now",
        "gameTag": post_data.gameTag,
        "liked": False
    }
    
    await db.posts.insert_one(new_post)
    return new_post

@api_router.put("/posts/{post_id}/like")
async def like_post(post_id: int, like_data: LikeRequest):
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    new_likes = post['likes'] + 1 if like_data.liked else post['likes'] - 1
    
    await db.posts.update_one(
        {"id": post_id},
        {"$set": {"likes": new_likes, "liked": like_data.liked}}
    )
    
    return {"likes": new_likes, "liked": like_data.liked}

@api_router.post("/posts/{post_id}/comments")
async def add_comment(post_id: int, comment_data: CommentRequest):
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    current_user = await db.users.find_one({"id": 1}, {"_id": 0})
    
    new_comment = {
        "id": len(post.get('comments', [])) + 1,
        "author": current_user['username'],
        "text": comment_data.text,
        "timestamp": "Just now"
    }
    
    await db.posts.update_one(
        {"id": post_id},
        {"$push": {"comments": new_comment}}
    )
    
    return new_comment

@api_router.put("/posts/{post_id}/share")
async def share_post(post_id: int):
    post = await db.posts.find_one({"id": post_id}, {"_id": 0})
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    new_shares = post['shares'] + 1
    
    await db.posts.update_one(
        {"id": post_id},
        {"$set": {"shares": new_shares}}
    )
    
    return {"shares": new_shares}

@api_router.get("/users", response_model=List[User])
async def get_users():
    users = await db.users.find({}, {"_id": 0}).to_list(1000)
    return users

@api_router.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@api_router.get("/users/{user_id}/posts", response_model=List[Post])
async def get_user_posts(user_id: int):
    posts = await db.posts.find({"userId": user_id}, {"_id": 0}).to_list(1000)
    return sorted(posts, key=lambda x: x['id'], reverse=True)

@api_router.get("/notifications", response_model=List[Notification])
async def get_notifications():
    notifications = await db.notifications.find({}, {"_id": 0}).to_list(1000)
    return notifications

@api_router.get("/current-user", response_model=User)
async def get_current_user():
    user = await db.users.find_one({"id": 1}, {"_id": 0})
    return user

app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/", StaticFiles(directory="/app/frontend", html=True), name="frontend")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()