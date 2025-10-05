export function setBasicAuth(username, password) {
  const token = btoa(`${username}:${password}`);
  localStorage.setItem("basic_token", token);
  return token;
}

export function clearAuth() {
  localStorage.removeItem("basic_token");
}

export function getAuthHeader() {
  const t = localStorage.getItem("basic_token");
  return t ? { Authorization: `Basic ${t}` } : {};
}

export function isLoggedIn() {
  return !!localStorage.getItem("basic_token");
}
