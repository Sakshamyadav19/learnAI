// Authentication utilities using localStorage

const AUTH_KEY = "learnai_auth";
const FASTINO_USER_ID_KEY = "learnai_fastino_user_id";

export interface AuthData {
  email: string;
  password: string;
  fastino_user_id?: string;
}

export const storeAuth = (email: string, password: string, fastino_user_id?: string): void => {
  const authData: AuthData = { email, password, fastino_user_id };
  localStorage.setItem(AUTH_KEY, JSON.stringify(authData));
};

export const getFastinoUserId = (): string | null => {
  // First try to get from auth data
  const auth = getAuth();
  if (auth?.fastino_user_id) {
    return auth.fastino_user_id;
  }
  
  // Fallback to separate key for backward compatibility
  const userId = localStorage.getItem(FASTINO_USER_ID_KEY);
  return userId;
};

export const setFastinoUserId = (user_id: string): void => {
  // Store in auth data
  const auth = getAuth();
  if (auth) {
    auth.fastino_user_id = user_id;
    localStorage.setItem(AUTH_KEY, JSON.stringify(auth));
  }
  
  // Also store separately for backward compatibility
  localStorage.setItem(FASTINO_USER_ID_KEY, user_id);
};

export const getAuth = (): AuthData | null => {
  const authString = localStorage.getItem(AUTH_KEY);
  if (!authString) return null;
  try {
    return JSON.parse(authString) as AuthData;
  } catch {
    return null;
  }
};

export const isAuthenticated = (): boolean => {
  return getAuth() !== null;
};

export const clearAuth = (): void => {
  localStorage.removeItem(AUTH_KEY);
};

