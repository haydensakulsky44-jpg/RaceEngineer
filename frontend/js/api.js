// api.js — centralise les appels au backend RaceEngineer et la gestion du token JWT.

// ⚠️ En développement local, laisse cette valeur telle quelle.
// En production, remplace-la par l'URL de ton backend déployé
// (ex: "https://api.raceengineer.app").
const API_BASE_URL = "http://localhost:8000";

const TOKEN_KEY = "raceengineer_token";

function saveToken(token) {
    localStorage.setItem(TOKEN_KEY, token);
}

function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

function clearToken() {
    localStorage.removeItem(TOKEN_KEY);
}

function isLoggedIn() {
    return Boolean(getToken());
}

async function apiRegister(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.detail || "Impossible de créer le compte.");
    }

    return data;
}

async function apiLogin(email, password) {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.detail || "Email ou mot de passe incorrect.");
    }

    saveToken(data.access_token);
    return data;
}

async function apiChat(message) {
    const token = getToken();

    const response = await fetch(`${API_BASE_URL}/chat`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message }),
    });

    if (response.status === 401) {
        // Token absent/expiré : on renvoie proprement vers la connexion
        clearToken();
        window.location.href = "login.html";
        throw new Error("Session expirée.");
    }

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.detail || "Une erreur est survenue.");
    }

    return data;
}

function logout() {
    clearToken();
    window.location.href = "login.html";
}

// Redirige vers la connexion si on n'est pas authentifié, en conservant
// l'URL voulue (ex: chat.html?exemple=...) pour y revenir après connexion.
function requireAuth() {
    if (!isLoggedIn()) {
        const destination = window.location.pathname.split("/").pop() + window.location.search;
        window.location.href = `login.html?redirect=${encodeURIComponent(destination)}`;
    }
}
