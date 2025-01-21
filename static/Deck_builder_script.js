// Sélectionnez les conteneurs
const availableCards = document.querySelectorAll('#available-card img');
const deckContainer = document.getElementById('deck-card');

// Ajout des événements aux cartes disponibles
availableCards.forEach(card => {
  card.addEventListener('dragstart', handleDragStart);
  card.addEventListener('dragend', handleDragEnd);
  card.addEventListener('click', handleCardClick);
});

// Ajout des événements au conteneur de deck
deckContainer.addEventListener('dragover', handleDragOver);
deckContainer.addEventListener('drop', handleDrop);

// Ajout d'un événement global pour détecter les drops en dehors
document.addEventListener('dragover', handleGlobalDragOver);
document.addEventListener('drop', handleOutsideDrop);

// Variables pour stocker la carte en cours de déplacement
let draggedCard = null;

// Stockage des cartes ajoutées dans le deck (limite de 3 exemplaires)
const cardCount = {};

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
}

// Autoriser le drag sur le conteneur
function handleDragOver(event) {
  event.preventDefault(); // Nécessaire pour permettre le drop
}

// Lâcher la carte dans le conteneur
function handleDrop(event) {
  event.preventDefault(); // Empêche le comportement par défaut du navigateur
  if (draggedCard) {
    const cardId = draggedCard.dataset.id;

    if (!cardCount[cardId]) {
      cardCount[cardId] = 0;
    }

    if (cardCount[cardId] >= 3) {
      alert('Vous ne pouvez pas ajouter plus de 3 exemplaires.');
      return;
    }

    const cardClone = draggedCard.cloneNode(true); // Clone la carte
    cardClone.setAttribute('draggable', false); // Empêche de glisser à nouveau
    cardClone.classList.remove('dragging'); // Nettoie les styles

    // Ajout d'un gestionnaire de clic pour supprimer la carte
    cardClone.addEventListener('click', handleDeckCardClick);

    // Ajout d'un événement de dragstart pour re-draguer hors du deck
    cardClone.addEventListener('dragstart', handleDragStart);

    deckContainer.appendChild(cardClone); // Ajoute au conteneur de deck
    cardCount[cardId]++;
  }
  draggedCard = null; // Réinitialise la variable
}

// Gestionnaire de clic pour ajouter une carte
function handleCardClick(event) {
  const clickedCard = event.target; // La carte cliquée
  const cardId = clickedCard.dataset.id;

  // Vérifier si la limite de 3 exemplaires par carte est atteinte
  if (!cardCount[cardId]) {
    cardCount[cardId] = 0; // Initialise la carte si elle n'existe pas
  }
  if (cardCount[cardId] >= 3) {
    alert('Vous ne pouvez pas ajouter plus de 3 exemplaires de cette carte.');
    return;
  }

  const cardClone = clickedCard.cloneNode(true); // Clone la carte
  cardClone.setAttribute('draggable', true); // Permet de la glisser à nouveau
  cardClone.classList.remove('dragging'); // Nettoie les styles

  // Ajout d'un gestionnaire de clic pour supprimer la carte
  cardClone.addEventListener('click', handleDeckCardClick);

  // Ajout d'un événement de dragstart pour re-draguer hors du deck
  cardClone.addEventListener('dragstart', handleDragStart);

  deckContainer.appendChild(cardClone); // Ajoute au conteneur de deck
  cardCount[cardId]++; // Incrémente le compteur de cette carte
}

// Gestionnaire de clic pour supprimer une carte du deck
function handleDeckCardClick(event) {
  const clickedCard = event.target; // La carte cliquée dans le deck
  const cardId = clickedCard.dataset.id;

  deckContainer.removeChild(clickedCard); // Supprime la carte du deck
  cardCount[cardId]--; // Décrémente le compteur de cette carte
}

// Gestionnaire global pour empêcher le comportement par défaut du dragover
function handleGlobalDragOver(event) {
  event.preventDefault(); // Empêche les comportements inattendus
}

// Gestionnaire pour supprimer une carte si elle est glissée en dehors du conteneur
function handleOutsideDrop(event) {
  if (draggedCard && !deckContainer.contains(event.target)) {
    const cardId = draggedCard.dataset.id;

    // Vérifier si la carte fait partie du deck avant de la supprimer
    if (deckContainer.contains(draggedCard)) {
      deckContainer.removeChild(draggedCard); // Supprime la carte du deck
      cardCount[cardId]--; // Décrémente le compteur de cette carte
    }
  }
  draggedCard = null; // Réinitialise la variable
}
