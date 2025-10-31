import instance from './axios';

// Easyappz API: Auth layer strictly per openapi.yml
// - POST /api/auth/login/
// - POST /api/auth/register/
// - GET  /api/auth/me/

export async function login(payload) {
  // payload: { username: string, password: string }
  const response = await instance.post('/api/auth/login/', payload);
  return response.data;
}

export async function register(payload) {
  // payload: { username: string, password: string }
  const response = await instance.post('/api/auth/register/', payload);
  return response.data;
}

export async function me() {
  const response = await instance.get('/api/auth/me/');
  return response.data;
}
