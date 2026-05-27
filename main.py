# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services import book_ride, create_new_user,register_new_driver,get_ride_history_by_passenger# Added new imports

app = FastAPI(title="Metro-Ride Backend API")

# --- DATA MODELS ---
class BookingRequest(BaseModel):
    passenger_id: int
    driver_id: int
    pickup_address: str
    dropoff_address: str
    fare: float

class UserCreateRequest(BaseModel):
    name: str
    email: str

class DriverUpdateRequest(BaseModel):
    name: str
    license_number: str

class DriverRegisterRequest(BaseModel):
    name: str
    license_number: str
    vehicle_type: str
    phone_number: str
# --- ENDPOINTS ---

@app.get("/")
def home():
    return {"message": "Welcome to Metro-Ride Backend API!"}

# 1. User Account Creation Endpoint
@app.post("/users")
def api_create_user(request: UserCreateRequest):
    user_id = create_new_user(request.name, request.email)
    if user_id:
        return {"status": "success", "user_id": user_id, "message": "User created successfully!"}
    else:
        raise HTTPException(status_code=400, detail="Could not create user. Email might already exist.")
# Inside main.py

@app.post("/drivers")
def api_register_driver(request: DriverRegisterRequest):
    try:
        # Feed all 5 pieces of data into your database function
        driver_id = register_new_driver(
            name=request.name,
            license_number=request.license_number,
            vehicle_type=request.vehicle_type,
            phone_number=request.phone_number
        )
        return {"status": "success", "driver_id": driver_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# # 2. Driver Profile Update Endpoint
# @app.put("/drivers/{driver_id}")
# def api_update_driver(driver_id: int, request: DriverUpdateRequest):
#     success = update_driver_profile(driver_id, request.name, request.license_number)
#     if success:
#         return {"status": "success", "message": f"Driver {driver_id} profile updated."}
#     else:
#         raise HTTPException(status_code=500, detail="Failed to update driver profile.")

# 3. Existing Ride Booking Endpoint
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
    
 # main.py
# (Make sure to add book_ride_auto to your app.services imports at the top!)
from app.services import book_ride_auto 

# 1. Create a request model that doesn't ask for a driver_id
class AutoBookingRequest(BaseModel):
    passenger_id: int
    pickup_address: str
    dropoff_address: str
    fare: float

# 2. Add the intelligent dispatch endpoint
@app.post("/bookings/auto-match")
def api_auto_match_ride(request: AutoBookingRequest):
    try:
        assignment = book_ride_auto(
            passenger_id=request.passenger_id,
            pickup=request.pickup_address,
            dropoff=request.dropoff_address,
            fare=request.fare
        )
        
        # If assignment is None, it means all drivers are busy!
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# main.py
# (Add complete_ongoing_ride to your app.services imports at the top!)
from app.services import complete_ongoing_ride

class CompleteRideRequest(BaseModel):
    driver_id: int

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
    
# main.py
# (Remember to add get_user_ride_history to your app.services imports at the top!)
from app.services import get_user_ride_history

# @app.get("/users/{user_id}/history")
# def api_get_ride_history(user_id: int):
#     try:
#         history = get_user_ride_history(user_id)
        
#         # If the user exists but has never booked a ride, return an empty list gracefully
#         return {
#             "status": "success",
#             "user_id": user_id,
#             "total_rides": len(history),
#             "history": history
#         }
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

# Make sure you are importing your database session generator correctly
# from config.database import get_db 
# Import the logic function we just created above
#from app.services import get_ride_history_by_passenger
from config.database import get_db_connection
# ... your existing routes like app.post("/users") or app.post("/bookings/auto-match") ...
from app.services import get_ride_history_by_passenger

# ... your other routes ...

# @app.get("/users/{passenger_id}/history")
# def get_passenger_history(passenger_id: int):
#     """
#     Exposes your live trip history array to the frontend.
#     """
#     return get_ride_history_by_passenger(passenger_id=passenger_id)


from fastapi import HTTPException
# Ensure your imports at the top look clean:
from app.services import get_user_ride_history, get_ride_history_by_passenger

# ==========================================
# 1. PASSENGER/USER HISTORY ENDPOINT
# ==========================================
@app.get("/users/{user_id}/history")
def api_get_user_history(user_id: int):
    """
    Fetches history records specifically for a Passenger/User.
    """
    try:
        history = get_user_ride_history(user_id)
        return {
            "status": "success",
            "user_id": user_id,
            "total_rides": len(history),
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==========================================
# 2. DRIVER HISTORY ENDPOINT (Changed path!)
# ==========================================
@app.get("/drivers/{driver_id}/history")
def api_get_driver_history(driver_id: int):
    """
    Fetches history records specifically for a Driver.
    """
    try:
        # Assuming get_ride_history_by_passenger was meant to target drivers, 
        # or you have a matching driver service function:
        history = get_ride_history_by_passenger(driver_id) 
        return {
            "status": "success",
            "driver_id": driver_id,
            "total_rides": len(history),
            "history": history
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))