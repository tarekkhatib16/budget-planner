// localStorage keeps the login across app restarts (important for a
// home-screen PWA). Trade-off: tokens in localStorage are readable by any
// JS on the page — acceptable here because we serve no third-party scripts.
const KEY = 'budget-planner-token';

export function getToken(): string | null {
  return localStorage.getItem(KEY);
}

export function setToken(token: string): void {
  localStorage.setItem(KEY, token);
}

export function clearToken(): void {
  localStorage.removeItem(KEY);
}
