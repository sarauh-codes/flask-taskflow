from datetime import date, timedelta

from website import db
from website.models import Task, User
from website.stats import task_stats
from tests.conftest import signup, logout

TODAY = date(2030, 6, 1)


def make_user(app, email):
    with app.app_context():
        user = User(email=email, password='x', first_name='Test')
        db.session.add(user)
        db.session.commit()
        return user.id


def add(app, user_id, title, priority='medium', status='pending', due_date=None):
    with app.app_context():
        db.session.add(Task(title=title, priority=priority, status=status,
                            due_date=due_date, user_id=user_id))
        db.session.commit()


def test_counts_by_status_and_priority(app):
    user_id = make_user(app, 'a@example.com')
    add(app, user_id, 'One', priority='low', status='pending')
    add(app, user_id, 'Two', priority='high', status='in_progress')
    add(app, user_id, 'Three', priority='high', status='completed')

    with app.app_context():
        stats = task_stats(user_id, today=TODAY)

    assert stats['total'] == 3
    assert stats['completed'] == 1
    assert stats['by_status'] == {'pending': 1, 'in_progress': 1, 'completed': 1}
    assert stats['by_priority'] == {'low': 1, 'medium': 0, 'high': 2}


def test_completion_rate(app):
    user_id = make_user(app, 'a@example.com')
    add(app, user_id, 'One', status='completed')
    add(app, user_id, 'Two', status='pending')
    add(app, user_id, 'Three', status='pending')
    add(app, user_id, 'Four', status='pending')

    with app.app_context():
        assert task_stats(user_id, today=TODAY)['completion_rate'] == 25


def test_empty_stats(app):
    user_id = make_user(app, 'a@example.com')

    with app.app_context():
        stats = task_stats(user_id, today=TODAY)

    assert stats['total'] == 0
    assert stats['completion_rate'] == 0
    assert stats['overdue'] == 0


def test_overdue_excludes_completed_and_undated(app):
    user_id = make_user(app, 'a@example.com')
    past = TODAY - timedelta(days=2)
    add(app, user_id, 'Late', status='pending', due_date=past)
    add(app, user_id, 'Late but in progress', status='in_progress', due_date=past)
    add(app, user_id, 'Late but done', status='completed', due_date=past)
    add(app, user_id, 'Due later', status='pending', due_date=TODAY + timedelta(days=1))
    add(app, user_id, 'No date', status='pending')

    with app.app_context():
        assert task_stats(user_id, today=TODAY)['overdue'] == 2


def test_stats_only_include_the_given_user(app):
    owner_id = make_user(app, 'owner@example.com')
    other_id = make_user(app, 'other@example.com')
    add(app, owner_id, 'Mine', status='completed')
    add(app, other_id, 'Theirs', status='pending')

    with app.app_context():
        stats = task_stats(owner_id, today=TODAY)

    assert stats['total'] == 1
    assert stats['completed'] == 1


def test_dashboard_requires_login(client):
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/login' in response.headers['Location']


def test_dashboard_shows_stats_and_chart_data(client):
    signup(client)
    client.post('/tasks/new', data={'title': 'Done thing', 'priority': 'high',
                                    'status': 'completed', 'due_date': ''})
    client.post('/tasks/new', data={'title': 'Open thing', 'priority': 'low',
                                    'status': 'pending', 'due_date': ''})

    response = client.get('/dashboard')
    html = response.get_data(as_text=True)

    assert response.status_code == 200
    assert 'id="stat-total">2<' in html
    assert 'id="stat-completed">1<' in html
    assert '"completed": 1' in html
    assert 'chart.umd.min.js' in html


def test_dashboard_empty_state(client):
    signup(client)
    response = client.get('/dashboard')

    assert b'No tasks yet.' in response.data
    assert b'id="statusChart"' not in response.data


def test_dashboard_is_per_user(client):
    signup(client, email='owner@example.com')
    client.post('/tasks/new', data={'title': 'Secret', 'priority': 'low',
                                    'status': 'pending', 'due_date': ''})
    logout(client)

    signup(client, email='other@example.com')
    response = client.get('/dashboard')
    assert b'id="stat-total">0<' in response.data
