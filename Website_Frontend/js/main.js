// Charge le header et le footer
document.addEventListener("DOMContentLoaded", function () {
    // Charger le Header
    fetch('partials/header.html')
        .then(response => {
            if (!response.ok) {
                throw new Error('Header non trouvé');
            }
            return response.text();
        })
        .then(data => {
            document.getElementById('header-placeholder').innerHTML = data;
        })
        .catch(error => console.error('Erreur chargement header:', error));


    // Charger le Footer
    fetch('partials/footer.html')
        .then(response => {
            if (!response.ok) {
                throw new Error('Footer non trouvé');
            }
            return response.text();
        })
        .then(data => {
            document.getElementById('footer-placeholder').innerHTML = data;
        })
        .catch(error => console.error('Erreur chargement footer:', error));
});

// faire apparaitre la box :"login"
const userButton = document.getElementById('userButton');
const loginBox = document.getElementById('loginBox');

userButton.addEventListener('click', () => {
    const isBoxVisible = loginBox.style.display === 'block';
    loginBox.style.display = isBoxVisible ? 'none' : 'block';
});

//menu déroulant pour mobile
const navToggle = document.querySelector('.nav-toggle');
const navLinks = document.querySelector('.nav-links');

// Affichage ou masquage des liens
navToggle.addEventListener('click', () => {
    navLinks.classList.toggle('active');
});

