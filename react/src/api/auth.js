import instance from './axios';

export const auth = {
  async login({ username, password }) {
    const { data } = await instance.post('/api/auth/login/', { username, password });
    return data;
  },
  async register({ username, password }) {
    const { data } = await instance.post('/api/auth/register/', { username, password });
    return data;
  },
  async me() {
    const { data } = await instance.get('/api/auth/me/');
    return data;
  },
};

export default auth;
