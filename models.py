from sqlalchemy import Table, Column, Integer, String, MetaData, Float

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
    Column("id", Integer, primary_key=True),
    Column("destination", String),
    Column("origin", String),
    Column("price", Float),
    Column("airline", String),
    Column("departure_date", String),
    Column("return_date", String, nullable=True),
)