from sqlalchemy import create_engine
import pandas as pd

db_user = "postgres"
db_password = "1234"
db_host = "localhost"
db_port = "5432"
db_name = "postgres"

SECRET_KEY = "vws80kzedXgWvtxVngsEewhcK1RRTy8VRxssHSW1yPFj6YxrFkZTEdMYeM9_Q48v"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES = 15  # minutes
REFRESH_TOKEN_EXPIRES = 7  # days
