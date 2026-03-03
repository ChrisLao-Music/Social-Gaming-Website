import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

users_data = [
    {
        "id": 1,
        "username": "NeonRider",
        "handle": "@neon_rider",
        "avatar": "https://images.unsplash.com/photo-1684488646170-62c5403733e4",
        "bio": "🎮 Pro Gamer | 🔥 Esports Enthusiast | 💜 Valorant Main",
        "followers": 2400,
        "following": 318,
        "isOnline": True
    },
    {
        "id": 2,
        "username": "Alex_Pro",
        "handle": "@alex_pro",
        "avatar": "https://images.unsplash.com/photo-1638581777063-bf3ed0496c67",
        "bio": "🏆 Champion Player | Streaming Daily",
        "followers": 1850,
        "following": 245,
        "isOnline": True
    },
    {
        "id": 3,
        "username": "Mia_Stream",
        "handle": "@mia_plays",
        "avatar": "https://images.unsplash.com/photo-1616702577619-0522a1f8d938",
        "bio": "✨ Content Creator | Mobile Legends Pro",
        "followers": 3200,
        "following": 892,
        "isOnline": False
    }
]

posts_data = [
    {
        "id": 101,
        "userId": 2,
        "username": "Alex_Pro",
        "handle": "@alex_pro",
        "avatar": "https://images.unsplash.com/photo-1638581777063-bf3ed0496c67",
        "content": "Just won my first tournament! 🏆 The grind never stops. Shoutout to my team! #Valorant #Esports",
        "image": "https://images.unsplash.com/photo-1642345843526-6279c8880a49",
        "likes": 342,
        "comments": [],
        "shares": 28,
        "timestamp": "2h ago",
        "gameTag": "Valorant",
        "liked": False
    },
    {
        "id": 102,
        "userId": 3,
        "username": "Mia_Stream",
        "handle": "@mia_plays",
        "avatar": "https://images.unsplash.com/photo-1616702577619-0522a1f8d938",
        "content": "Epic comeback in ranked! Down 0-2 and clutched it 3-2! 💪🔥 #MLBB #MobileLegends",
        "image": "https://images.unsplash.com/photo-1728632286888-04c64f48e506",
        "likes": 189,
        "comments": [],
        "shares": 15,
        "timestamp": "4h ago",
        "gameTag": "MLBB",
        "liked": False
    },
    {
        "id": 103,
        "userId": 1,
        "username": "NeonRider",
        "handle": "@neon_rider",
        "avatar": "https://images.unsplash.com/photo-1684488646170-62c5403733e4",
        "content": "New gaming setup complete! RGB everything 🌈💜 Ready to dominate! #GamingSetup #PCGaming",
        "image": "https://images.unsplash.com/photo-1688407832489-cc9db90773f5",
        "likes": 456,
        "comments": [],
        "shares": 42,
        "timestamp": "6h ago",
        "gameTag": "League of Legends",
        "liked": False
    },
    {
        "id": 104,
        "userId": 2,
        "username": "Alex_Pro",
        "handle": "@alex_pro",
        "avatar": "https://images.unsplash.com/photo-1638581777063-bf3ed0496c67",
        "content": "Anyone up for some late night ranked matches? Looking for a squad! 🎮 #CODMobile #TeamUp",
        "image": None,
        "likes": 67,
        "comments": [],
        "shares": 8,
        "timestamp": "8h ago",
        "gameTag": "COD Mobile",
        "liked": False
    },
    {
        "id": 105,
        "userId": 3,
        "username": "Mia_Stream",
        "handle": "@mia_plays",
        "avatar": "https://images.unsplash.com/photo-1616702577619-0522a1f8d938",
        "content": "Streaming in 30 minutes! Come hang out and let's push to Diamond together! 💎✨ #LiveStream #ApexLegends",
        "image": None,
        "likes": 234,
        "comments": [],
        "shares": 19,
        "timestamp": "12h ago",
        "gameTag": "Apex Legends",
        "liked": False
    }
]

notifications_data = [
    {
        "id": 1,
        "type": "like",
        "user": "Alex_Pro",
        "avatar": "https://images.unsplash.com/photo-1638581777063-bf3ed0496c67",
        "text": "liked your post",
        "time": "5m ago"
    },
    {
        "id": 2,
        "type": "follow",
        "user": "Mia_Stream",
        "avatar": "https://images.unsplash.com/photo-1616702577619-0522a1f8d938",
        "text": "started following you",
        "time": "1h ago"
    },
    {
        "id": 3,
        "type": "comment",
        "user": "Alex_Pro",
        "avatar": "https://images.unsplash.com/photo-1638581777063-bf3ed0496c67",
        "text": "commented on your post",
        "time": "2h ago"
    }
]

async def seed_database():
    print("Clearing existing data...")
    await db.users.delete_many({})
    await db.posts.delete_many({})
    await db.notifications.delete_many({})
    
    print("Seeding users...")
    await db.users.insert_many(users_data)
    
    print("Seeding posts...")
    await db.posts.insert_many(posts_data)
    
    print("Seeding notifications...")
    await db.notifications.insert_many(notifications_data)
    
    print("✅ Database seeded successfully!")
    client.close()

if __name__ == "__main__":
    asyncio.run(seed_database())