document.addEventListener('DOMContentLoaded', function() {
  const deleteButton = document.getElementById('deleteButton');

  deleteButton.addEventListener('click', function(event) {
      // Empêche la soumission immédiate du formulaire
      event.preventDefault();

      // Affiche la fenêtre de confirmation
      var confirmAction = confirm("Are you sure you want to delete your account?");

      // Si l'utilisateur confirme, soumettre le formulaire
      if (confirmAction) {
          // Soumet le formulaire de suppression
          deleteButton.form.submit();
      }
  });
});
