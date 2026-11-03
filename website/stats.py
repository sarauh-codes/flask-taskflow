from datetime import date

from sqlalchemy import func

from . import db
from .models import Task, PRIORITIES, STATUSES


def task_stats(user_id, today=None):
    """Summarise one user's tasks for the dashboard."""
    today = today or date.today()

    by_status = dict.fromkeys(STATUSES, 0)
    by_priority = dict.fromkeys(PRIORITIES, 0)
    counts = (db.session.query(Task.status, Task.priority, func.count(Task.id))
              .filter(Task.user_id == user_id)
              .group_by(Task.status, Task.priority)
              .all())
    for status, priority, count in counts:
        by_status[status] += count
        by_priority[priority] += count

    total = sum(by_status.values())
    overdue = (Task.query
               .filter(Task.user_id == user_id,
                       Task.due_date < today,
                       Task.status != 'completed')
               .count())

    return {
        'total': total,
        'completed': by_status['completed'],
        'overdue': overdue,
        'completion_rate': round(by_status['completed'] / total * 100) if total else 0,
        'by_status': by_status,
        'by_priority': by_priority,
    }
