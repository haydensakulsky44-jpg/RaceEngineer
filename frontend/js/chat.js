// chat.js — logique de l'interface de chat (page protégée par requireAuth()).

requireAuth();

const journal = document.getElementById("journal");
const form = document.getElementById("form-saisie");
const input = document.getElementById("saisie-message");
const indicateur = document.getElementById("indicateur-frappe");
const suggestions = document.getElementById("suggestions");
const boutonNouveauChat = document.getElementById("bouton-nouveau-chat");

const MESSAGE_ACCUEIL =
    "Bienvenue au stand. Pose-moi une question sur l'orientation, le setup, un circuit, les règles de course, ta préparation, ou la télémétrie — et si ça sort de ce cadre, je fais de mon mieux quand même, tant que ça reste sport auto.";

function horodatage() {
    const maintenant = new Date();
    return maintenant.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" });
}

function ajouterMessage(role, texte) {
    const message = document.createElement("div");
    message.className = `message ${role}`;

    const etiquette = document.createElement("div");
    etiquette.className = "message-etiquette";
    etiquette.textContent =
        role === "utilisateur"
            ? `TOI · ${horodatage()}`
            : role === "systeme"
            ? "SYSTÈME"
            : `RACEENGINEER · ${horodatage()}`;

    const contenu = document.createElement("div");
    contenu.className = "message-contenu";
    contenu.textContent = texte;

    message.appendChild(etiquette);
    message.appendChild(contenu);
    journal.appendChild(message);

    journal.scrollTop = journal.scrollHeight;
}

async function envoyerMessage(texte) {
    if (!texte) return;

    suggestions.classList.add("cachee");

    ajouterMessage("utilisateur", texte);
    input.value = "";
    input.disabled = true;
    indicateur.textContent = "RaceEngineer réfléchit...";

    try {
        const data = await apiChat(texte);
        ajouterMessage("assistant", data.response);
    } catch (err) {
        ajouterMessage("systeme", `⚠️ ${err.message}`);
    } finally {
        input.disabled = false;
        indicateur.textContent = "";
        input.focus();
    }
}

function nouveauChat() {
    journal.innerHTML = "";
    suggestions.classList.remove("cachee");
    ajouterMessage("assistant", MESSAGE_ACCUEIL);
    input.value = "";
    input.focus();
}

form.addEventListener("submit", (event) => {
    event.preventDefault();
    envoyerMessage(input.value.trim());
});

suggestions.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
        envoyerMessage(chip.dataset.exemple);
    });
});

boutonNouveauChat.addEventListener("click", nouveauChat);

// Démarrage : message d'accueil, puis on envoie automatiquement une
// question d'exemple si on arrive via un lien externe (ex: ?exemple=...).
ajouterMessage("assistant", MESSAGE_ACCUEIL);

(function envoyerExempleSiPresent() {
    const params = new URLSearchParams(window.location.search);
    const exemple = params.get("exemple");
    if (!exemple) return;

    window.history.replaceState({}, "", "chat.html");
    envoyerMessage(exemple);
})();
