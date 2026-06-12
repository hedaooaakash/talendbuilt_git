# ETL Platform Command Reference

## Docker
docker ps
docker ps -a
docker start oracle-xe
docker stop oracle-xe
docker restart oracle-xe
docker logs oracle-xe --tail 50

## Oracle Verification
cd D:\ETLPlatform
python test_oracle.py
python verify_tables.py

## FastAPI
uvicorn app.main:app --reload

Swagger:
http://localhost:8000/docs

## Python Dependencies
pip install fastapi uvicorn oracledb passlib[bcrypt] python-jose
pip list
pip freeze > requirements.txt
pip install -r requirements.txt

## Database Scripts
python create_tables.py
python test_password.py
python verify_tables.py

## Daily Startup
docker start oracle-xe
docker ps
cd D:\ETLPlatform
python test_oracle.py
uvicorn app.main:app --reload

## Troubleshooting
docker ps -a
docker logs oracle-xe
netstat -ano | findstr 1522
python --version
pip show oracledb

## Project Status
Completed:
- Oracle XE Docker Setup
- Oracle Connectivity
- USERS table
- PIPELINES table
- JOBS table
- Password Hashing

Next:
- Register API
- Login API
- JWT Authentication
- Protected Endpoints
