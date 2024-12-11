from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import timedelta, datetime, date
from typing import Optional, List
from sqlalchemy import select, insert
from database import database

from models import flight_packages
from admin_auth import (AdminLogin, Token, authenticate_admin, AdminRegister, get_password_hash,
                        create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, admin_users)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.on_event("startup")
async def startup():
    if not database.is_connected:
        await database.connect()


@app.on_event("shutdown")
async def shutdown():
    if database.is_connected:
        await database.disconnect()


class FlightPackage(BaseModel):
    id: int
    name: str
    destination: str
    origin: str
    price: float
    airline: str
    departure_date: date
    return_date: Optional[date] = None
    date_created: datetime = None



@app.post('/admin/register', response_model=Token)
async def register_admin(admin_register: AdminRegister):
    query = select(admin_users).where(admin_users.c.username == admin_register.username)
    existing_admin = await database.fetch_one(query)
    if existing_admin:
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(admin_register.password)
    query = insert(admin_users).values(username=admin_register.username, hashed_password=hashed_password)
    await database.execute(query)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": admin_register.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}


@app.post('/admin/login', response_model=Token)
async def login_admin(admin_login: AdminLogin):
    if not await authenticate_admin(admin_login.username, admin_login.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": admin_login.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "message": "Admin authenticated"}


@app.post('/flight/package', response_model=FlightPackage)
async def create_flight_package(package: FlightPackage):
    try:
        query = insert(flight_packages).values(
            destination=package.destination,
            origin=package.origin,
            price=package.price,
            airline=package.airline,
            departure_date=package.departure_date,
            return_date=package.return_date
        ).returning(flight_packages.c.id)
        last_record_id = await database.execute(query)
        return {**package.dict(), "id": last_record_id,
                "message": f"Flight package successfully created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/flight/packages', response_model=List[FlightPackage])
async def list_flight_packages():
    query = select(flight_packages)
    try:
        results = await database.fetch_all(query)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get('/flight/package/{package_id}', response_model=FlightPackage)
async def get_flight_package(package_id: int):
    query = select(flight_packages).where(flight_packages.c.id == package_id)
    result = await database.fetch_one(query)
    if result is None:
        raise HTTPException(status_code=404, detail="Flight package not found")
    return result


@app.put('/flight/package/{package_id}', response_model=FlightPackage)
async def update_flight_package(package_id: int, package: FlightPackage):
    query = select(flight_packages).where(flight_packages.c.id == package_id)
    existing_package = await database.fetch_one(query)
    if existing_package is None:
        raise HTTPException(status_code=404, detail="Flight package not found")

    update_query = flight_packages.update().where(flight_packages.c.id == package_id).values(
        destination=package.destination,
        origin=package.origin,
        price=package.price,
        airline=package.airline,
        departure_date=package.departure_date,
        return_date=package.return_date
    )
    await database.execute(update_query)
    return {**package.dict(), "id": package_id, "message": f"Flight package with id {package_id} successfully updated"}


@app.delete('/flight/package/{package_id}', response_model=FlightPackage)
async def drop_flight_package(package_id: int, package: FlightPackage):
    query = select(flight_packages).where(flight_packages.c.id == package_id)
    existing_package = await database.fetch_one(query)
    if existing_package is None:
        raise HTTPException(status_code=404, detail="Flight package not found")

    delete_query = flight_packages.delete().where(flight_packages.c.id == package_id)
    await database.execute(delete_query)
    return {**package.dict(), "id": package_id, "message": f"Flight package with id {package_id} successfully deleted"}


@app.get('/flight/search', response_model=List[FlightPackage])
async def search_flight_packages(
        destination: Optional[str] = Query(None),
        origin: Optional[str] = Query(None),
        min_price: Optional[float] = Query(None),
        max_price: Optional[float] = Query(None),
        airline: Optional[str] = Query(None),
        departure_date: Optional[str] = Query(None),
        return_date: Optional[str] = Query(None)
):
    query = select(flight_packages)
    if destination:
        query = query.where(flight_packages.c.destination == destination)
    if origin:
        query = query.where(flight_packages.c.origin == origin)
    if min_price:
        query = query.where(flight_packages.c.price >= min_price)
    if max_price:
        query = query.where(flight_packages.c.price <= max_price)
    if airline:
        query = query.where(flight_packages.c.airline == airline)
    if departure_date:
        query = query.where(flight_packages.c.departure_date == departure_date)
    if return_date:
        query = query.where(flight_packages.c.return_date == return_date)

    results = await database.fetch_all(query)
    return results


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='0.0.0.0', port=8000)
