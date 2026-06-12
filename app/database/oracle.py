import os
import oracledb
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return oracledb.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        host=os.getenv("ORACLE_HOST"),
        port=int(os.getenv("ORACLE_PORT")),
        service_name=os.getenv("ORACLE_SERVICE")
    )