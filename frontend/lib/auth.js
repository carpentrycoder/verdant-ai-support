const TOKEN_KEY = 'verdant_agent_access_token';


export function getAccessToken() {
  if (typeof window === 'undefined') {
    return null;
  }

  return sessionStorage.getItem(TOKEN_KEY);
}


export function setAccessToken(token) {
  if (typeof window === 'undefined') {
    return;
  }

  sessionStorage.setItem(
    TOKEN_KEY,
    token
  );
}


export function removeAccessToken() {
  if (typeof window === 'undefined') {
    return;
  }

  sessionStorage.removeItem(
    TOKEN_KEY
  );
}


export function isAuthenticated() {
  return Boolean(
    getAccessToken()
  );
}