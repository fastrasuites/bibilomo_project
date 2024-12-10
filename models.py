from datetime import datetime

from sqlalchemy import Table, Date, Column, Integer, String, MetaData, Float, DateTime

metadata = MetaData()

admin_users = Table(
    "admin_users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True, nullable=False),
    Column("hashed_password", String, nullable=False),
)

flight_packages = Table(
    "flight_packages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("destination", String),
    Column("origin", String),
    Column("price", Float),
    Column("airline", String),
    Column("date_created", DateTime, default=datetime.utcnow),
    Column("departure_date", Date),
    Column("return_date", Date, nullable=True),
)