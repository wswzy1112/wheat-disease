/**
 * API configuration - Centralized API management
 * Update API_BASE_URL to point to your production server
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

export function getToken() {
  return localStorage.getItem('auth_token')
}

export function setToken(token) {
  localStorage.setItem('auth_token', token)
}

export function clearToken() {
  localStorage.removeItem('auth_token')
  localStorage.removeItem('user_id')
  localStorage.removeItem('username')
}

export { API_BASE_URL }
export default { API_BASE_URL, getToken, setToken, clearToken }
