### Create docker for Taxi App
```
docker run -d --name project -p 5458:5432 \
-e POSTGRES_USER=user \
-e POSTGRES_PASSWORD=password \
-e POSTGRES_DB=taxi_app_db \
postgres
```

### Connect docker
```
psql -h 127.0.0.1 -p 5458 -U user taxi_app_db
```
