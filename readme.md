# Queue manager Backend

รัน server ด้วยคำสั่ง
```
uvicorn main:app --reload
```


# The data table used
```sql
CREATE TABLE queue (
            id INTEGER PRIMARY KEY,
            create_date DATETIME,
            ip TEXT,
            call_id INTEGER,
            category TEXT,
            warehouse TEXT,
            enter_time DATETIME,
            exit_time DATETIME
        );
```