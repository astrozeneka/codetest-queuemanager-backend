import os
import sqlite3
from datetime import datetime


class QueueDataManager:
    # Singleton design pattern
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(QueueDataManager, cls).__new__(cls)
        return cls._instance

    connection = None
    def __init__(self, connection):
        """CREATE TABLE queue (
            id INTEGER PRIMARY KEY,
            create_date DATETIME,
            ip TEXT,
            call_id INTEGER,
            category TEXT,
            warehouse TEXT,
            enter_time DATETIME,
            exit_time DATETIME
        );"""
        self.connection = connection

    def getCollectionByCategory(self, category):
        self.connection = sqlite3.connect(os.getenv('DB_PATH') or 'db.sqlite3')
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM queue WHERE category=?", (category,))
        rows = cursor.fetchall()
        output = []
        for row in rows:
            output.append({
                'id': row[0],
                'create_date': row[1],
                'ip': row[2],
                'call_id': row[3],
                'category': row[4],
                'warehouse': row[5],
                'enter_time': row[6],
                'exit_time': row[7]
            })
        return output

    def getAwaitingCollectionByCategory(self, category):
        self.connection = sqlite3.connect(os.getenv('DB_PATH') or 'db.sqlite3')
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM queue WHERE category=? AND enter_time IS ''", (category,))
        rows = cursor.fetchall()
        output = []
        for row in rows:
            output.append({
                'id': row[0],
                'create_date': row[1],
                'ip': row[2],
                'call_id': row[3],
                'category': row[4],
                'warehouse': row[5],
                'enter_time': row[6],
                'exit_time': row[7]
            })
        return output

    def getOne(self, id):
        self.connection = sqlite3.connect(os.getenv('DB_PATH') or 'db.sqlite3')
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM queue WHERE id=?", (id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return {
            'id': row[0],
            'create_date': row[1],
            'ip': row[2],
            'call_id': row[3],
            'category': row[4],
            'warehouse': row[5],
            'enter_time': row[6],
            'exit_time': row[7]
        }

    def insert(self, queue):
        self.connection = sqlite3.connect(os.getenv('DB_PATH') or 'db.sqlite3')
        # Request the last inserted queue in the same category
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM queue WHERE category=? ORDER BY id DESC LIMIT 1", (queue['category'],))
        last_queue = cursor.fetchone()
        if last_queue is None or last_queue[3] is None:
            next_id = 1
        else:
            next_id = last_queue[3] + 1

        # Insert in the database
        cursor = self.connection.cursor()
        queue['create_date'] = datetime.now()
        queue['ip'] = ''
        queue['call_id'] = next_id
        queue['warehouse'] = ''
        queue['enter_time'] = ''
        queue['exit_time'] = ''
        print(last_queue)
        print(next_id)
        print(queue)
        queue = (queue['create_date'], queue['ip'], queue['call_id'], queue['category'], queue['warehouse'], queue['enter_time'], queue['exit_time'])
        cursor.execute("INSERT INTO queue (create_date, ip, call_id, category, warehouse, enter_time, exit_time) VALUES (?, ?, ?, ?, ?, ?, ?)", queue)
        self.connection.commit()
        return cursor.lastrowid

    def processQueue(self, id, warehouse):
        # Get the queue
        queue = self.getOne(id)
        queue['enter_time'] = 'now'
        queue['warehouse'] = warehouse
        self.update(queue)
        queue = self.getOne(id)
        return queue

    def update(self, queue):
        self.connection = sqlite3.connect(os.getenv('DB_PATH') or 'db.sqlite3')
        cursor = self.connection.cursor()
        queue = (queue['create_date'], queue['ip'], queue['call_id'], queue['category'], queue['warehouse'], queue['enter_time'], queue['exit_time'], queue['id'])
        cursor.execute("UPDATE queue SET create_date=?, ip=?, call_id=?, category=?, warehouse=?, enter_time=?, exit_time=? WHERE id=?", queue)
        self.connection.commit()
        return cursor.lastrowid

    def getCalledQueue(self):
        # All queue that have already a enter_time
        self.connection = sqlite3.connect(os.getenv('DB_PATH') or 'db.sqlite3')
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM queue WHERE enter_time IS NOT '' ORDER BY id DESC LIMIT 10")
        rows = cursor.fetchall()
        output = []
        for row in rows:
            output.append({
                'id': row[0],
                'create_date': row[1],
                'ip': row[2],
                'call_id': row[3],
                'category': row[4],
                'warehouse': row[5],
                'enter_time': row[6],
                'exit_time': row[7]
            })
        return output

    def getCalledQueueByCategory(self, category):
        # All queue that have already a enter_time
        self.connection = sqlite3.connect(os.getenv('DB_PATH') or 'db.sqlite3')
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM queue WHERE category=? AND enter_time IS NOT '' ORDER BY id DESC LIMIT 10", (category,))
        rows = cursor.fetchall()
        output = []
        for row in rows:
            output.append({
                'id': row[0],
                'create_date': row[1],
                'ip': row[2],
                'call_id': row[3],
                'category': row[4],
                'warehouse': row[5],
                'enter_time': row[6],
                'exit_time': row[7]
            })
        return output