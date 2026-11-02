from datetime import date, timedelta

from website import db
from website.models import Task
from tests.conftest import signup, logout


def task_form(**overrides):
    data = {
        'title': 'Write report',
        'description': 'Quarterly numbers',
        'priority': 'high',
        'status': 'pending',
        'due_date': '2030-01-15',
    }
    data.update(overrides)
    return data


def get_task(app, title):
    with app.app_context():
        task = Task.query.filter_by(title=title).first()
        return task and {
            'id': task.id,
            'title': task.title,
            'description': task.description,
            'priority': task.priority,
            'status': task.status,
            'due_date': task.due_date,
            'user_id': task.user_id,
        }


def count_tasks(app):
    with app.app_context():
        return Task.query.count()


def test_home_requires_login(client):
    response = client.get('/')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_signup_logs_user_in(client):
    signup(client)
    assert client.get('/').status_code == 200


def test_create_task(client, app):
    signup(client)
    response = client.post('/tasks/new', data=task_form())

    assert response.status_code == 302
    task = get_task(app, 'Write report')
    assert task['priority'] == 'high'
    assert task['status'] == 'pending'
    assert task['due_date'] == date(2030, 1, 15)


def test_create_task_without_due_date(client, app):
    signup(client)
    client.post('/tasks/new', data=task_form(due_date=''))

    assert get_task(app, 'Write report')['due_date'] is None


def test_new_task_page_renders(client):
    signup(client)
    response = client.get('/tasks/new')
    assert response.status_code == 200
    assert b'New Task' in response.data


def test_create_task_requires_title(client, app):
    signup(client)
    response = client.post('/tasks/new', data=task_form(title='   '))

    assert response.status_code == 200
    assert b'Title is required.' in response.data
    assert count_tasks(app) == 0


def test_create_task_rejects_invalid_priority(client, app):
    signup(client)
    response = client.post('/tasks/new', data=task_form(priority='urgent'))

    assert b'Choose a valid priority.' in response.data
    assert count_tasks(app) == 0


def test_create_task_rejects_invalid_status(client, app):
    signup(client)
    response = client.post('/tasks/new', data=task_form(status='done'))

    assert b'Choose a valid status.' in response.data
    assert count_tasks(app) == 0


def test_create_task_rejects_invalid_due_date(client, app):
    signup(client)
    response = client.post('/tasks/new', data=task_form(due_date='15/01/2030'))

    assert b'Due date must be a valid date.' in response.data
    assert count_tasks(app) == 0


def test_home_lists_tasks(client):
    signup(client)
    client.post('/tasks/new', data=task_form(title='Buy milk'))

    response = client.get('/')
    assert b'Buy milk' in response.data


def test_edit_task_changes_priority_and_status(client, app):
    signup(client)
    client.post('/tasks/new', data=task_form())
    task_id = get_task(app, 'Write report')['id']

    response = client.post(f'/tasks/{task_id}/edit', data=task_form(priority='low', status='completed'))

    assert response.status_code == 302
    task = get_task(app, 'Write report')
    assert task['priority'] == 'low'
    assert task['status'] == 'completed'


def test_edit_page_prefills_existing_values(client, app):
    signup(client)
    client.post('/tasks/new', data=task_form())
    task_id = get_task(app, 'Write report')['id']

    response = client.get(f'/tasks/{task_id}/edit')
    assert b'value="Write report"' in response.data
    assert b'value="2030-01-15"' in response.data


def test_edit_with_invalid_data_keeps_original(client, app):
    signup(client)
    client.post('/tasks/new', data=task_form())
    task_id = get_task(app, 'Write report')['id']

    client.post(f'/tasks/{task_id}/edit', data=task_form(title=''))

    assert get_task(app, 'Write report') is not None


def test_delete_task(client, app):
    signup(client)
    client.post('/tasks/new', data=task_form())
    task_id = get_task(app, 'Write report')['id']

    response = client.post(f'/tasks/{task_id}/delete')

    assert response.status_code == 302
    assert count_tasks(app) == 0


def test_cannot_edit_or_delete_another_users_task(client, app):
    signup(client, email='owner@example.com')
    client.post('/tasks/new', data=task_form())
    task_id = get_task(app, 'Write report')['id']
    logout(client)

    signup(client, email='intruder@example.com')
    assert client.get(f'/tasks/{task_id}/edit').status_code == 404
    assert client.post(f'/tasks/{task_id}/edit', data=task_form(title='Hacked')).status_code == 404
    assert client.post(f'/tasks/{task_id}/delete').status_code == 404

    task = get_task(app, 'Write report')
    assert task is not None
    assert task['title'] == 'Write report'
    assert task['user_id'] != get_intruder_id(app)


def get_intruder_id(app):
    with app.app_context():
        from website.models import User
        return User.query.filter_by(email='intruder@example.com').first().id


def test_overdue_flag(app):
    with app.app_context():
        past = Task(title='Late', due_date=date.today() - timedelta(days=1), status='pending', user_id=1)
        done = Task(title='Done late', due_date=date.today() - timedelta(days=1), status='completed', user_id=1)
        future = Task(title='Future', due_date=date.today() + timedelta(days=1), status='pending', user_id=1)
        assert past.is_overdue is True
        assert done.is_overdue is False
        assert future.is_overdue is False
        assert Task(title='No date', user_id=1).is_overdue is False
