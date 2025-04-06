from sqlalchemy import create_engine
import pandas as pd

db_user = "postgres"
db_password = "1234"
db_host = "localhost"
db_port = "5432"
db_name = "postgres"

SECRET_KEY = "86467b0635b3824bc703b2eb76da4cc23d3e4ad31ee74c8b83a0cf5b88f0f7a84265e1bcb4f62cc567685bf9419adc1d8d3c2a67d160d8d0f7d15493a5456be3"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRES = 15  # minutes
REFRESH_TOKEN_EXPIRES = 7  # days
