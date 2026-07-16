// Получаем элемент .features-title
const featuresTitle = document.querySelector('.features-title');

// Добавляем обработчик события на клик
featuresTitle.addEventListener('click', function() {
    // Переключаем класс 'active' для элемента
    this.classList.toggle('active');
});


document.addEventListener("DOMContentLoaded", function () {
    const menuButton = document.querySelector(".navbar-toggler");
    const menuIcon = document.getElementById("menuIcon");

    menuButton.addEventListener("click", function () {
        setTimeout(() => {
            const isExpanded = this.getAttribute("aria-expanded") === "true";
            menuIcon.src = isExpanded ? this.dataset.open : this.dataset.close;
        }, 10); // Короткая задержка, чтобы Bootstrap успел обновить атрибут
    });
});
