// API Configuration
// In development, this is empty (uses Vite proxy).
// In production (Firebase/Vercel), this should point to the live backend URL.
// Example: https://world-tour-backend.onrender.com

// Use environment variable if set, otherwise use production backend URL for production builds
const getApiBaseUrl = () => {
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl) return envUrl;
  
  // Production backend URL - update this if your backend URL changes
  if (import.meta.env.PROD) {
    return 'https://world-tour-ngmj.onrender.com';
  }
  
  // Development - empty string uses Vite proxy
  return '';
};

export const API_BASE_URL = getApiBaseUrl();
