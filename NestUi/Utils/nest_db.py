import asyncio
from datetime import datetime
from prisma import Prisma

# This decorator automatically opens a Prisma context and passes the db object to your function.
def prisma_wrapper(func):
    async def wrapper(*args, **kwargs):
        async with Prisma() as db:
            return await func(db, *args, **kwargs)
    return wrapper


# This decorator allows an async function to be called in a synchronous context.
def run_sync(func):
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper

# Create a new Buoy record.
# Note: Using `long_val` instead of `long` because `long` is a Python built-in.
@run_sync
@prisma_wrapper
async def create_buoy(db, lat: float, long_val: float, battery: int, drop_time: datetime):
    return await db.buoy.create(
        data={
            "lat": lat,
            "long": long_val,
            "battery": battery,
            "drop_time": drop_time,
        }
    )

# Retrieve a Buoy record by its buoy_id.
@run_sync
@prisma_wrapper
async def get_buoy_by_id(db, buoy_id: int):
    return await db.buoy.find_unique(
        where={"buoy_id": buoy_id}
    )

# Update a Buoy record.
@run_sync
@prisma_wrapper
async def update_buoy(db, buoy_id: int, update_data: dict):
    return await db.buoy.update(
        where={"buoy_id": buoy_id},
        data=update_data,
    )

# Delete a Buoy record.
@run_sync
@prisma_wrapper
async def delete_buoy(db, buoy_id: int):
    return await db.buoy.delete(
        where={"buoy_id": buoy_id}
    )

# List all Buoy records.
@run_sync
@prisma_wrapper
async def list_buoys(db):
    return await db.buoy.find_many()