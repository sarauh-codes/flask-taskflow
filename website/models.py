from datetime import date

from . import db
from flask_login import UserMixin

PRIORITIES = ('low', 'medium', 'high')
STATUSES = ('pending', 'in_progress', 'completed')


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    tasks = db.relationship('Task', backref='owner', cascade='all, delete-orphan')


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, default='')
    priority = db.Column(db.String(10), nullable=False, default='medium')
    status = db.Column(db.String(20), nullable=False, default='pending')
    due_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime(timezone=True), default=db.func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    @property
    def is_overdue(self):
        return self.due_date is not None and self.status != 'completed' and self.due_date < date.today()
