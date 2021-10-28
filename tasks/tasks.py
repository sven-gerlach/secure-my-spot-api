"""
Celery application file
"""

from celery import Celery


app = Celery("tasks", broker="amqp://guest:guest@rabbit:5672//")


@app.task
def add(x, y):
    return x + y
