document.addEventListener("DOMContentLoaded", () => {
  const descriptions = {
      "zone-deck": "C'est ici que vous piochez vos cartes au début de chaque tour.",
      "zone-cimetiere": "Zone où vont les cartes détruites ou utilisées.",
      "zone-main": "Cartes que vous avez en main, prêtes à être jouées.",
      "zone-equipement": "Placez ici vos cartes équipement et amélioration.",
      "zone-piege": "Ici placez vos pièges face verso, pour surprendre votre opposant.",
      "zone-action": "Lieu où vous placez et effectuez vos actions d'attaque ou de défense.",
  };

  function showInfo(zoneId) {
      document.getElementById("info-text").innerText = descriptions[zoneId] || "Zone inconnue.";
      document.getElementById("info-box").style.display = "block";
  }

  function hideInfo() {
      document.getElementById("info-box").style.display = "none";
  }

  // Attacher l'événement de clic à chaque zone interactive
  document.querySelectorAll(".zone").forEach(zone => {
      zone.addEventListener("click", () => showInfo(zone.id));
  });

  // Attacher l'événement de fermeture
  document.getElementById("close-info").addEventListener("click", hideInfo);
});
