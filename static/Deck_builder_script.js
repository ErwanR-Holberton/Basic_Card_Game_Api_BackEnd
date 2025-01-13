// Sélectionnez les conteneurs
const availableCards = document.querySelectorAll('#available-card img');
const deckContainer = document.getElementById('deck-card');

// Ajout des événements aux cartes disponibles
availableCards.forEach(card => {
  card.addEventListener('dragstart', handleDragStart);
  card.addEventListener('dragend', handleDragEnd);
});

// Ajout des événements au conteneur de deck
deckContainer.addEventListener('dragover', handleDragOver);
deckContainer.addEventListener('drop', handleDrop);

// Variables pour stocker la carte en cours de déplacement
let draggedCard = null;

// Début du drag
function handleDragStart(event) {
  draggedCard = event.target;
  event.dataTransfer.setData('text/plain', draggedCard.dataset.id);
  event.dataTransfer.effectAllowed = 'move'; // Optionnel : améliore l'UX
  draggedCard.classList.add('dragging'); // Ajout d'une classe pour le style
}

// Fin du drag
function handleDragEnd(event) {
  draggedCard.classList.remove('dragging'); // Supprime la classe
  draggedCard = null; // Réinitialise la variable
}

// Autoriser le drag sur le conteneur
function handleDragOver(event) {
  event.preventDefault(); // Nécessaire pour permettre le drop
}

// Lâcher la carte dans le conteneur
function handleDrop(event) {
  event.preventDefault(); // Empêche le comportement par défaut du navigateur
  if (draggedCard) {
    const cardClone = draggedCard.cloneNode(true); // Clone la carte
    cardClone.setAttribute('draggable', false); // Empêche de glisser à nouveau
    cardClone.classList.remove('dragging'); // Nettoie les styles
    deckContainer.appendChild(cardClone); // Ajoute au conteneur de deck
  }
}
