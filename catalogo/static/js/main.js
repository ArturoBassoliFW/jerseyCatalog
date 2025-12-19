document.addEventListener('DOMContentLoaded', function() {
    const toggleButton = document.querySelector('.mobile-menu-toggle');
    const menu = document.querySelector('.navbar-menu');
    const body = document.body;

    if (toggleButton && menu) {
        toggleButton.addEventListener('click', function() {
            
            // 1. Logica di apertura/chiusura
            menu.classList.toggle('is-open');
            body.classList.toggle('no-scroll'); 
            toggleButton.classList.toggle('is-active');

            const isExpanded = toggleButton.getAttribute('aria-expanded') === 'true' || false;
            toggleButton.setAttribute('aria-expanded', !isExpanded);
            
            // 2. Logica di cambio icona (TESTUALE)
            if (menu.classList.contains('is-open')) {
                toggleButton.innerHTML = '✕'; // Icona di chiusura
            } else {
                toggleButton.innerHTML = '☰'; // Icona del menu
            }
        });
    }
});