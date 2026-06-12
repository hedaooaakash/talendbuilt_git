from fastapi import APIRouter

from app.database.oracle import get_connection
from app.models.connection import ConnectionCreate

router = APIRouter(
    prefix="/connections",
    tags=["Connections"]
)

@router.post("/")
def create_connection(connection: ConnectionCreate):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO CONNECTIONS
        (
            NAME,
            TYPE,
            HOST,
            PORT,
            USERNAME,
            PASSWORD,
            DATABASE_NAME
        )
        VALUES
        (
            :1,
            :2,
            :3,
            :4,
            :5,
            :6,
            :7
        )
    """,
    [
        connection.name,
        connection.type,
        connection.host,
        connection.port,
        connection.username,
        connection.password,
        connection.database_name
    ])

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "Connection created successfully"
    }


@router.get("/")
def get_connections():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            ID,
            NAME,
            TYPE,
            HOST,
            PORT,
            USERNAME,
            DATABASE_NAME
        FROM CONNECTIONS
        ORDER BY ID
    """)

    rows = cursor.fetchall()

    result = []

    for row in rows:
        result.append({
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "host": row[3],
            "port": row[4],
            "username": row[5],
            "database_name": row[6]
        })

    cursor.close()
    conn.close()

    return result