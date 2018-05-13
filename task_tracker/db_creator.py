import MySQLdb
import random
import string

conn = MySQLdb.connect('127.0.0.1', 'root', '')
cursor = conn.cursor()

cursor.execute('CREATE DATABASE IF NOT EXISTS task_tracker')
cursor.execute('USE task_tracker')
cursor.execute("""CREATE TABLE IF NOT EXISTS
                      users (
                      id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                      first_name varchar(20),
                      second_name varchar(20))""")

cursor.execute("""CREATE TABLE IF NOT EXISTS
                      tasks (
                      id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
                      user_id int,
                      task varchar(100),
                      parent_task_id int,
                      status enum('new', 'in_process', 'done') not null
                      )""")

random_name = lambda: ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
for new_id in range(20):
    cursor.execute("INSERT into users (first_name, second_name) VALUES (%s, %s)", (random_name(), random_name()))

for task_id in range(15):
    cursor.execute("INSERT into tasks(task) VALUES (%s)", ('sit at home', ))

for subtask_id in range(16, 21):
    cursor.execute("INSERT into tasks(task, parent_task_id) VALUES (%s, %s)", ('take a carrot', random.randint(0, 15)))

conn.commit()
conn.close()
