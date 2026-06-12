from fastapi import APIRouter, HTTPException

from app.database.oracle import get_connection
from app.auth.security import hash_password, verify_password
from app.auth.jwt_handler import create_access_token
from app.models.user import UserRegister, UserLogin

router = APIRouter(tags=["Authentication"])

@router.post("/register")
def register(user: UserRegister):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT COUNT(*) FROM USERS WHERE EMAIL = :1",
        [user.email]
    )

    count = cursor.fetchone()[0]

    if count > 0:
        cursor.close()
        conn.close()

        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_password = hash_password(user.password)

    cursor.execute(
        """
        INSERT INTO USERS
        (EMAIL, PASSWORD_HASH)
        VALUES (:1, :2)
        """,
        [user.email, hashed_password]
    )

    conn.commit()

    cursor.close()
    conn.close()

    return {
        "message": "User registered successfully"
    }


@router.post("/login")
def login(user: UserLogin):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ID, EMAIL, PASSWORD_HASH
        FROM USERS
        WHERE EMAIL = :1
        """,
        [user.email]
    )

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if not result:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    user_id, email, password_hash = result

    if not verify_password(
        user.password,
        password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )

    token = create_access_token({
        "sub": str(user_id),
        "email": email
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }