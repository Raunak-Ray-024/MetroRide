from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Consolidated imports cleanly at the top
from app.services import (
    book_ride, 
    create_new_user, 
    register_new_driver, 
    book_ride_auto, 
    complete_ongoing_ride, 
    get_user_ride_history
)

app = FastAPI(title="Metro-Ride Backend API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In development, this allows your HTML file to communicate safely
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DATA MODELS ---
class BookingRequest(BaseModel):
    passenger_id: int
    driver_id: int
    pickup_address: str
    dropoff_address: str
    fare: float

class AutoBookingRequest(BaseModel):
    passenger_id: int
    pickup_address: str
    dropoff_address: str
    fare: float

class UserCreateRequest(BaseModel):
    name: str
    email: str

class DriverRegisterRequest(BaseModel):
    name: str
    license_number: str
    vehicle_type: str
    phone_number: str

class CompleteRideRequest(BaseModel):
    driver_id: int

# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"message": "Welcome to Metro-Ride Backend API!"}

# 1. User Account Creation Endpoint
@app.post("/users")
def api_create_user(request: UserCreateRequest):
    try:
        user_id = create_new_user(request.name, request.email)
        return {"status": "success", "user_id": user_id, "message": "User created successfully!"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Could not create user: {str(e)}")

# 2. Driver Registration Endpoint
@app.post("/drivers")
def api_register_driver(request: DriverRegisterRequest):
    try:
        driver_id = register_new_driver(
            name=request.name,
            license_number=request.license_number,
            vehicle_type=request.vehicle_type,
            phone_number=request.phone_number
        )
        return {"status": "success", "driver_id": driver_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 3. Manual Ride Booking Endpoint
@app.post("/book-ride")
def api_book_ride(request: BookingRequest):
    success = book_ride(
        request.passenger_id, request.driver_id, 
        request.pickup_address, request.dropoff_address, request.fare
    )
    if success:
        return {"status": "success", "message": "Ride successfully booked!"}
    else:
        raise HTTPException(status_code=500, detail="Booking failed.")
    
# 4. Intelligent Auto-Match Dispatch Endpoint
@app.post("/bookings/auto-match")
def api_auto_match_ride(request: AutoBookingRequest):
    try:
        assignment = book_ride_auto(
            passenger_id=request.passenger_id,
            pickup=request.pickup_address,
            dropoff=request.dropoff_address,
            fare=request.fare
        )
        
        if not assignment:
            raise HTTPException(
                status_code=404, 
                detail="No available drivers found nearby. Please try again in a few minutes!"
            )
            
        return {
            "status": "success",
            "message": "Driver found and dispatched successfully!",
            "booking_id": assignment["booking_id"],
            "assigned_driver_id": assignment["driver_id"]
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# 5. Complete Ride Endpoint
@app.patch("/bookings/{booking_id}/complete")
def api_complete_ride(booking_id: int, request: CompleteRideRequest):
    try:
        success = complete_ongoing_ride(booking_id, request.driver_id)
        if success:
            return {
                "status": "success",
                "message": f"Ride {booking_id} marked as completed. Driver {request.driver_id} is now free!"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 6. User Ride History Endpoint (Added matching route)
@app.get("/users/{user_id}/history")
def api_get_ride_history(user_id: int):
    try:
        history = get_user_ride_history(user_id)
        return {"status": "success", "history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))