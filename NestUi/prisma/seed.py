import asyncio
from datetime import datetime
from prisma import Prisma
from dotenv import load_dotenv

async def seed():
    async with Prisma() as db:
        # Optional: Delete all existing buoy records.
        # Be cautious with delete_many() in production environments.
        await db.buoy.delete_many()

        # Define sample buoy data to seed
        sample_buoys = [
            {
                "lat": 42.3601,
                "long": -71.0589,
                "battery": 95,
                "drop_time": datetime(2025, 2, 19, 12, 30, 0)
            },
            {
                "lat": 40.7128,
                "long": -74.0060,
                "battery": 80,
                "drop_time": datetime(2025, 2, 18, 11, 0, 0)
            },
            {
                "lat": 34.0522,
                "long": -118.2437,
                "battery": 70,
                "drop_time": datetime(2025, 2, 17, 14, 15, 0)
            }
        ]

        # Insert each buoy record into the database
        for buoy in sample_buoys:
            created_buoy = await db.buoy.create(data=buoy)
            print("Created buoy:", created_buoy)

if __name__ == '__main__':
    load_dotenv()
    asyncio.run(seed())