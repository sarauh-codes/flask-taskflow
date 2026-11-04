from tests.conftest import signup


def test_toggle_button_on_every_page(client):
    assert b'id="theme-toggle"' in client.get('/login').data
    assert b'id="theme-toggle"' in client.get('/signup').data


def test_saved_theme_is_applied_before_paint(client):
    html = client.get('/login').get_data(as_text=True)
    assert "localStorage.getItem('theme') === 'dark'" in html
    assert 'dark-mode' in html


def test_theme_assets_are_served(client):
    css = client.get('/static/style.css')
    js = client.get('/static/theme.js')

    assert css.status_code == 200
    assert b'html.dark-mode' in css.data
    assert js.status_code == 200
    assert b'theme-toggle' in js.data


def test_dashboard_includes_chart_dark_mode_hook(client):
    signup(client)
    html = client.get('/dashboard').get_data(as_text=True)
    assert "classList.contains('dark-mode')" in html
