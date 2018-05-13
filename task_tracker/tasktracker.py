import MySQLdb


class TaskTracker:

    def __init__(self):
        self.db = MySQLdb.connect('127.0.0.1', 'root', '', 'task_tracker')
        self.cursor = self.db.cursor()

    def add_task(self, task, parent_task_id='NULL'):
        self.cursor.execute("INSERT into tasks(task, parent_task_id) VALUES (%s, %s)", (task, parent_task_id))
        self.cursor.execute("SELECT LAST_INSERT_ID(), task FROM tasks where id=LAST_INSERT_ID()")
        self.db.commit()
        return self.cursor.fetchone()

    def get_status(self, task_id):
        self.cursor.execute("SELECT status FROM tasks WHERE id = %s", (task_id, ))
        current_status = self.cursor.fetchone()
        if current_status is None:
            raise ValueError("This id isn't in the db")
        return current_status[0]

    def take_task(self, user_id, task_id):

        def recursive_finding_and_processing(_user_id, _task_id):

            self.cursor.execute("SELECT status FROM tasks WHERE id = %s", (_task_id, ))
            current_status = self.cursor.fetchone()
            if current_status[0] == 'new':
                self.cursor.execute("UPDATE tasks SET status = 'in_process', user_id = %s where id = %s", (_user_id, _task_id))
            else:
                raise RuntimeError('This task has already status {}'.format(current_status[0]))

            self.cursor.execute('SELECT * FROM tasks WHERE parent_task_id = %s', (_task_id, ))
            tasks = self.cursor.fetchall()
            for task in tasks:
                parent_task_id = task[3]
                current_task_id = task[0]
                if parent_task_id != _task_id:
                    continue
                recursive_finding_and_processing(user_id, current_task_id)

        recursive_finding_and_processing(user_id, task_id)
        self.db.commit()

    def mark_task_as_done(self, task_id):

        def recursive_marking(_task_id):
            self.cursor.execute("UPDATE tasks SET status = 'done' where id = %s", (_task_id, ))
            self.cursor.execute('SELECT * FROM tasks WHERE parent_task_id = %s', (_task_id, ))
            tasks = self.cursor.fetchall()
            for task in tasks:
                parent_task_id = task[3]
                current_task_id = task[0]
                if parent_task_id != _task_id:
                    continue
                recursive_marking(current_task_id)

        recursive_marking(task_id)
        self.db.commit()

    def __del__(self):
        self.db.close()
