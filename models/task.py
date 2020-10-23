import asyncio
from datetime import datetime

from data import query


class Task:
    def __init__(self, task_key: str):
        self.task_key = task_key

    def get_task_state(self) -> str:
        tasks = []
        cur = query(f"SELECT task_state FROM tasks WHERE task_key like '{self.task_key}';")
        for row in cur.fetchall():
            tasks.append(row[0])
        if not tasks:
            return self.get_task_state()
        return tasks[0]

    def create_task(self):
        cur_date = datetime.now()
        query(
            f"Insert into tasks (task_key, task_state, date_created) values ({self.task_key}, 'False', '{cur_date}');")

    async def complete_task(self):
        await asyncio.sleep(0)
        cur_date = datetime.now()
        query(f"Update tasks set task_state='True', date_finished='{cur_date}' WHERE task_key like '{self.task_key}';")
