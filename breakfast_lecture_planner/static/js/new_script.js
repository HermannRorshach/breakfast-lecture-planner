const featuresTitle = document.querySelector(".features-title");
const submenuWrapper = featuresTitle?.querySelector(".submenu_wrapper");

if (featuresTitle && submenuWrapper) {
    let closeMenuTimeout;

    const openMenu = () => {
        clearTimeout(closeMenuTimeout);
        featuresTitle.classList.add("hover-active");
    };

    const closeMenuLater = () => {
        clearTimeout(closeMenuTimeout);
        closeMenuTimeout = setTimeout(() => {
            featuresTitle.classList.remove("hover-active");
        }, 500);
    };

    // Keep the menu open while the pointer crosses the gap between its title
    // and the absolutely positioned submenu.
    featuresTitle.addEventListener("mouseenter", openMenu);
    featuresTitle.addEventListener("mouseleave", closeMenuLater);
    submenuWrapper.addEventListener("mouseenter", openMenu);
    submenuWrapper.addEventListener("mouseleave", closeMenuLater);

    // Preserve the existing option to toggle the desktop menu by clicking it.
    featuresTitle.addEventListener("click", (event) => {
        if (event.target.closest(".submenu_wrapper")) {
            return;
        }

        featuresTitle.classList.toggle("active");
    });
}


document.addEventListener("DOMContentLoaded", function () {
    const menuButton = document.querySelector(".navbar-toggler");
    const menuIcon = document.getElementById("menuIcon");

    if (!menuButton || !menuIcon) {
        return;
    }

    menuButton.addEventListener("click", function () {
        setTimeout(() => {
            const isExpanded = this.getAttribute("aria-expanded") === "true";
            menuIcon.src = isExpanded ? this.dataset.open : this.dataset.close;
        }, 10); // Короткая задержка, чтобы Bootstrap успел обновить атрибут
    });
});
