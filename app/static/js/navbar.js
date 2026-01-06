document.querySelectorAll('[data-toggle="dropdown"]').forEach(btn => {
  btn.addEventListener('click', (e) => {
    e.preventDefault();
    const menu = btn.nextElementSibling;
    if (menu.classList.contains('show')) {
      menu.classList.remove('show');
    } else {
      // Sluit andere menu's
      document.querySelectorAll('.dropdown-menu.show').forEach(m => {
        if (m !== menu) m.classList.remove('show');
      });
      menu.classList.add('show');
    }
  });
});

// Sluit menu als je buiten klikt
document.addEventListener('click', (e) => {
  if (!e.target.closest('.navbar-account') && !e.target.closest('.navbar-plus')) {
    document.querySelectorAll('.dropdown-menu.show').forEach(m => {
      m.classList.remove('show');
    });
  }
});