const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'

export async function login({ email, password }) {
  const resp = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, password })
  })

  const json = await resp.json().catch(() => ({}))

  if (!resp.ok) {
    const message = json?.message || 'Login failed'
    throw new Error(message)
  }

  // json.data is expected according to APIResponse.success
  return json.data
}

export function saveTokens(tokens = {}, admin = {}) {
  if (tokens.access_token) localStorage.setItem('access_token', tokens.access_token)
  if (tokens.refresh_token) localStorage.setItem('refresh_token', tokens.refresh_token)
  if (admin) localStorage.setItem('admin', JSON.stringify(admin))
}

export function getAccessToken() {
  return localStorage.getItem('access_token')
}

export function getRefreshToken() {
  return localStorage.getItem('refresh_token')
}

export function getAdmin() {
  const raw = localStorage.getItem('admin')
  try {
    return raw ? JSON.parse(raw) : null
  } catch (e) {
    return null
  }
}

export function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('admin')
}

export async function authFetch(input, init = {}) {
  const headers = new Headers(init.headers || {})
  const token = getAccessToken()
  if (token) headers.set('Authorization', `Bearer ${token}`)
  init.headers = headers
  return fetch(input, init)
}
