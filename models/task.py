import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

from data import query


class Task:
    def __init__(self, task_id: str):
        self.task_id = task_id

    def create_task(self) -> None:
        """
        Create a new task in the database
        """
        sql = """
        INSERT INTO tasks (task_id, status, created_at) 
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        status = VALUES(status), 
        created_at = VALUES(created_at)
        """
        params = (self.task_id, 'pending', datetime.now())
        query(sql, parameters=params)

    def get_task_state(self) -> str:
        """
        Retrieve the current state of the task

        Returns:
            Task status as a string (pending, completed, failed)
        """
        sql = "SELECT status FROM tasks WHERE task_id = %s"
        try:
            rows = query(sql, parameters=(self.task_id,))

            # If no rows found, create a pending task
            if not rows:
                self.create_task()
                return "pending"

            # Return status, defaulting to 'pending'
            return rows[0].get('status', 'pending')

        except Exception as e:
            print(f"Error retrieving task state: {e}")
            return "pending"

    async def complete_task(self) -> None:
        """
        Mark the task as completed
        """
        sql = """
        UPDATE tasks 
        SET status = %s, completed_at = %s 
        WHERE task_id = %s
        """
        params = ('completed', datetime.now(), self.task_id)

        try:
            query(sql, parameters=params)
        except Exception as e:
            print(f"Error completing task {self.task_id}: {e}")

    async def fail_task(self, error_message: str = "") -> None:
        """
        Mark the task as failed
        """
        sql = """
        UPDATE tasks 
        SET status = %s, completed_at = %s, error_message = %s
        WHERE task_id = %s
        """
        params = ('failed', datetime.now(), error_message, self.task_id)

        try:
            query(sql, parameters=params)
        except Exception as e:
            print(f"Error marking task as failed {self.task_id}: {e}")