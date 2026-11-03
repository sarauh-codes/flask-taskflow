from website import db
from website.models import Task
from tests.conftest import signup, logout


def add_task(client, title, priority='medium', status='pending'):
    client.post('/tasks/new', data={
        'title': title,
        'description': '',
        'priority': priority,
        'status': status,
        'due_date': '',
    })


def titles_on_page(response):
    """Return the task titles shown in the list, in order."""
    html = response.get_data(as_text=True)
    return [title for title in ('Buy milk', 'Write report', 'Call mom', 'Fix bike') if f'>{title}<' in html]


def seed(client):
    add_task(client, 'Buy milk', priority='low', status='pending')
    add_task(client, 'Write report', priority='high', status='in_progress')
    add_task(client, 'Call mom', priority='high', status='completed')
    add_task(client, 'Fix bike', priority='medium', status='pending')


def test_search_matches_title_case_insensitively(client):
    signup(client)
    seed(client)

    response = client.get('/?q=REPORT')
    assert titles_on_page(response) == ['Write report']


def test_search_with_partial_match(client):
    signup(client)
    seed(client)

    response = client.get('/?q=bi')
    assert titles_on_page(response) == ['Fix bike']


def test_filter_by_priority(client):
    signup(client)
    seed(client)

    response = client.get('/?priority=high')
    assert sorted(titles_on_page(response)) == ['Call mom', 'Write report']


def test_filter_by_status(client):
    signup(client)
    seed(client)

    response = client.get('/?status=pending')
    assert sorted(titles_on_page(response)) == ['Buy milk', 'Fix bike']


def test_combined_filters(client):
    signup(client)
    seed(client)

    response = client.get('/?priority=high&status=completed')
    assert titles_on_page(response) == ['Call mom']


def test_no_matches_shows_filter_message(client):
    signup(client)
    seed(client)

    response = client.get('/?q=nothing-matches-this')
    assert b'No tasks match these filters.' in response.data


def test_invalid_filter_values_are_ignored(client):
    signup(client)
    seed(client)

    response = client.get('/?priority=urgent&status=whatever')
    assert len(titles_on_page(response)) == 4


def test_filters_only_show_current_users_tasks(client):
    signup(client, email='owner@example.com')
    add_task(client, 'Buy milk', priority='low')
    logout(client)

    signup(client, email='other@example.com')
    response = client.get('/?q=milk')
    assert b'No tasks match these filters.' in response.data


def test_filter_form_keeps_selected_values(client):
    signup(client)
    seed(client)

    response = client.get('/?q=report&priority=high&status=in_progress')
    assert b'value="report"' in response.data
    assert b'value="high" selected' in response.data
    assert b'value="in_progress" selected' in response.data
