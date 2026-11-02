from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from flask_login import login_required, current_user
from . import db
from .models import Task, PRIORITIES, STATUSES

views = Blueprint('views', __name__)


def _parse_task_form(form):
    """Validate the submitted task form. Returns (data, errors)."""
    title = (form.get('title') or '').strip()
    description = (form.get('description') or '').strip()
    priority = form.get('priority') or 'medium'
    status = form.get('status') or 'pending'
    due_raw = (form.get('due_date') or '').strip()

    errors = []
    if not title:
        errors.append('Title is required.')
    elif len(title) > 200:
        errors.append('Title must be 200 characters or fewer.')
    if priority not in PRIORITIES:
        errors.append('Choose a valid priority.')
    if status not in STATUSES:
        errors.append('Choose a valid status.')

    due_date = None
    if due_raw:
        try:
            due_date = date.fromisoformat(due_raw)
        except ValueError:
            errors.append('Due date must be a valid date.')

    data = {
        'title': title,
        'description': description,
        'priority': priority,
        'status': status,
        'due_date': due_date,
    }
    return data, errors


def _get_user_task(task_id):
    """Return the task if it belongs to the current user, otherwise 404."""
    task = db.session.get(Task, task_id)
    if task is None or task.user_id != current_user.id:
        abort(404)
    return task


@views.route('/')
@login_required
def home():
    tasks = (Task.query.filter_by(user_id=current_user.id)
             .order_by(Task.due_date.is_(None), Task.due_date, Task.id)
             .all())
    return render_template("home.html", user=current_user, tasks=tasks)


@views.route('/tasks/new', methods=['GET', 'POST'])
@login_required
def create_task():
    values = {'priority': 'medium', 'status': 'pending'}
    if request.method == 'POST':
        data, errors = _parse_task_form(request.form)
        if errors:
            for error in errors:
                flash(error, category='error')
            values = request.form
        else:
            task = Task(user_id=current_user.id, **data)
            db.session.add(task)
            db.session.commit()
            flash("Task created successfully!", category='success')
            return redirect(url_for('views.home'))
    return render_template("task_form.html", task=None, values=values,
                           priorities=PRIORITIES, statuses=STATUSES)


@views.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = _get_user_task(task_id)
    if request.method == 'POST':
        data, errors = _parse_task_form(request.form)
        if errors:
            for error in errors:
                flash(error, category='error')
            values = request.form
        else:
            for field, value in data.items():
                setattr(task, field, value)
            db.session.commit()
            flash("Task updated successfully!", category='success')
            return redirect(url_for('views.home'))
    else:
        values = {
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'status': task.status,
            'due_date': task.due_date.isoformat() if task.due_date else '',
        }
    return render_template("task_form.html", task=task, values=values,
                           priorities=PRIORITIES, statuses=STATUSES)


@views.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = _get_user_task(task_id)
    db.session.delete(task)
    db.session.commit()
    flash("Task deleted.", category='success')
    return redirect(url_for('views.home'))
