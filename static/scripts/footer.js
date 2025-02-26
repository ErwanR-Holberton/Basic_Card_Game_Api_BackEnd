document.addEventListener("DOMContentLoaded", function() {
  // Ouverture des modales
  document.querySelectorAll("[data-modal]").forEach(el => {
    el.addEventListener("click", function(event) {
      event.preventDefault(); // Empêche le comportement par défaut du lien
      const modal = document.getElementById(this.dataset.modal);
      if (modal) {
        modal.style.display = "block";
      }
    });
  });

  // Fermeture des modales via la croix
  document.querySelectorAll("[data-close]").forEach(el => {
    el.addEventListener("click", function() {
      const modal = document.getElementById(this.dataset.close);
      if (modal) {
        modal.style.display = "none";
      }
    });
  });

  // Fermeture des modales en cliquant en dehors de la modal
  window.addEventListener("click", function(event) {
    // Si l'utilisateur clique sur un lien pour ouvrir une modal, ne rien faire
    if (event.target.closest("[data-modal]")) return;

    // Parcours toutes les modales
    document.querySelectorAll('.modal').forEach(modal => {
      // Vérifie si l'élément cliqué est en dehors de la modal
      if (!modal.contains(event.target)) {
        modal.style.display = "none"; // Si on clique en dehors de la modal, on la ferme
      }
    });
  });
});
