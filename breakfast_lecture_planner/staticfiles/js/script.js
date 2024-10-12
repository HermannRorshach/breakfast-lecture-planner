// Открыть/закрыть боковое меню
document.getElementById('showMenu').onclick = () => {
    document.getElementById('sideMenu').classList.add('open');
  };
  document.getElementById('closeMenu').onclick = () => {
    document.getElementById('sideMenu').classList.remove('open');
  };