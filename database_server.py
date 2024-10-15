from fastapi import FastAPI, HTTPException, Depends
from fastapi import Request
from pydantic import BaseModel
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from typing import List, Optional
import json
from pathlib import Path

# Get the directory of the current file
current_dir = Path(__file__).resolve().parent
def load_json(filename):
    try:
        with open(filename, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: The file {filename} was not found.")
        return None
    except json.JSONDecodeError:
        print("Error: Failed to decode JSON.")
        return None

json_file_path = current_dir / "mongo_data" / "warehouse_data.json"
data = load_json(json_file_path)
app = FastAPI()

# Dependency to get the MongoDB client
async def get_db(request: Request):
    return request.app.state.db

@app.post("/init_db")
async def init_db(client: AsyncIOMotorClient = Depends(get_db)):
    # Clear collections
    await client.local.warehouse_db.drop()
    await client.local.transactions.drop()

    # Insert example data
    await client.local.warehouse_db.insert_many(example_data)

    return {"message": "Database initialized with example data."}

@app.on_event("startup")
async def startup_db_client():
    app.state.db = AsyncIOMotorClient("mongodb://localhost:27017")

@app.on_event("shutdown")
async def shutdown_db_client():
    app.state.db.close()

class ItemLocation(BaseModel):
    item_id: str

class TransactionModel(BaseModel):
    transaction_id: str
    item_id: str
    status: str  # e.g., 'in_transit', 'paid', 'aborted'

class Item(BaseModel):
    id: str
    name: str
    description: Optional[str] = None  # Make description optional
    category: str
    producer: str
    location: dict  # You can further specify this if you create a Location model
    quantity: int

    class Config:
        from_attributes = True

@app.get("/items", response_model=List[Item])
async def get_items(client: AsyncIOMotorClient = Depends(get_db)):
    items = []
    async for item in client.local.warehouse_db.find():
        item_dict = item.copy()  # Create a copy of the item
        item_dict['id'] = str(item_dict.pop('_id'))  # Convert ObjectId to string and rename the key
        items.append(Item(**item_dict))  # Use the Item model for serialization
    return items

@app.post("/items/search")
async def search_items(search_query: dict, client: AsyncIOMotorClient = Depends(get_db)):
    items = []
    async for item in client.local.warehouse_db.find(search_query):
        items.append(item)
    return items

# 1. Get product location by item_id
@app.get("/items/{item_id}/location")
async def get_item_location(item_id: str, client: AsyncIOMotorClient = Depends(get_db)):
    item = await client.local.warehouse_db.find_one({"_id": item_id})
    if item:
        return {"item_id": item_id, "location": item["location"]}
    raise HTTPException(status_code=404, detail="Item not found")

# 2. Track product transit status (with ability to abort)
@app.post("/transactions/start")
async def start_transaction(transaction: TransactionModel, client: AsyncIOMotorClient = Depends(get_db)):
    item = await client.local.warehouse_db.find_one({"_id": transaction.item_id})
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    new_transaction = {
        "transaction_id": transaction.transaction_id,
        "item_id": transaction.item_id,
        "status": "in_transit"  # Default status is 'in_transit'
    }
    await client.local.transactions.insert_one(new_transaction)
    return {"message": "Transaction started", "transaction": new_transaction}

# Abort a transaction
@app.put("/transactions/{transaction_id}/abort")
async def abort_transaction(transaction_id: str, client: AsyncIOMotorClient = Depends(get_db)):
    transaction = await client.local.transactions.find_one({"transaction_id": transaction_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    await client.local.transactions.update_one({"transaction_id": transaction_id}, {"$set": {"status": "aborted"}})
    return {"message": "Transaction aborted", "transaction_id": transaction_id}

# 3. Mark product as sold
@app.put("/transactions/{transaction_id}/complete")
async def complete_transaction(transaction_id: str, client: AsyncIOMotorClient = Depends(get_db)):
    transaction = await client.local.transactions.find_one({"transaction_id": transaction_id})
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction["status"] != "in_transit":
        raise HTTPException(status_code=400, detail="Transaction cannot be completed. Status: " + transaction["status"])

    await client.local.transactions.update_one({"transaction_id": transaction_id}, {"$set": {"status": "paid"}})
    await client.local.warehouse_db.update_one({"_id": transaction["item_id"]}, {"$inc": {"quantity": -1}})

    return {"message": "Transaction completed and item sold", "transaction_id": transaction_id}

if __name__ == "__main__":
    import asyncio
    import uvicorn

    # Run the FastAPI application
    asyncio.run(uvicorn.run(app, host="0.0.0.0", port=8000))