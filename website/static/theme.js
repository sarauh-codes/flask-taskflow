// Dark mode toggle. The saved choice is applied before paint by an inline script in base.html.
(function () {
  var STORAGE_KEY = 'theme';

  function isDark() {
    return document.documentElement.classList.contains('dark-mode');
  }

  function updateLabel(button) {
    button.textContent = isDark() ? 'Light mode' : 'Dark mode';
  }

  function save(value) {
    try {
      localStorage.setItem(STORAGE_KEY, value);
    } catch (e) {
      // Storage can be blocked (private mode, disabled cookies); the toggle still works for this page.
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    var button = document.getElementById('theme-toggle');
    if (!button) {
      return;
    }
    updateLabel(button);
    button.addEventListener('click', function () {
      document.documentElement.classList.toggle('dark-mode');
      save(isDark() ? 'dark' : 'light');
      updateLabel(button);
    });
  });
})();
