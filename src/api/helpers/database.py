from sqlalchemy import text, create_engine
import api.settings
import pandas as pd


class DataBase:
    def __init__(self):
        db_url = f"postgresql://{api.settings.db_user}:{api.settings.db_password}@{api.settings.db_host}:{api.settings.db_port}/{api.settings.db_name}"

        self.engine = create_engine(db_url)

    def Get(self, query, params={}):
        with self.engine.connect() as conn:
            res = pd.read_sql(text(query), conn, params=params)
            return res

    def Update(self, data, uid, table):
        with self.engine.begin() as conn:
            for key, val in data.items():
                conn.execute(
                    text(f"UPDATE {table} SET {key} = :val WHERE id = :id"),
                    {"val": val, "id": int(uid)},
                )
