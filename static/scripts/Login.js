document.addEventListener("DOMContentLoaded", function () {
  // Gestion du formulaire de connexion
  const login = document.querySelector('#login');
  const openLogin = document.querySelector('#login_button');
  const closeLogin = document.querySelector('#closeLogin');

  // Gestion du formulaire d'inscription
  const signup = document.querySelector('#signup');
  const openSignup = document.querySelector('#signup_button');
  const closeSignup = document.querySelector('#closeSignup');
  const signupForm = document.querySelector('form[action="/signup"]');
  const signpass = document.getElementById('signpass');
  const signpasscheck = document.getElementById('signpasscheck');
  const err = document.getElementById('signup_error_message');

  // Ouvrir/Fermer le login
  openLogin.addEventListener('click', () => { login.style.display = 'block'; });
  closeLogin.addEventListener('click', () => { login.style.display = 'none'; });

  // Ouvrir/Fermer le signup
  openSignup.addEventListener('click', () => { signup.style.display = 'block'; });
  closeSignup.addEventListener('click', () => { signup.style.display = 'none'; });

  // Fermer les overlays quand on clique en dehors
  window.addEventListener('click', (event) => { if (event.target === login) { login.style.display = 'none'; } });
  window.addEventListener('click', (event) => { if (event.target === signup) { signup.style.display = 'none'; } });

  // Vérification des mots de passe lors de l'inscription
  if (signupForm) {
    signupForm.addEventListener("submit", function (event) {
      if (signpass.value !== signpasscheck.value) {
        err.textContent = "Passwords do not match. Please try again.";
        err.style.display = "block";
        event.preventDefault(); // Empêcher la soumission du formulaire
      }
    });
  }
});
