import instance from './axios';

// Easyappz API: Listings layer strictly per openapi.yml
// - GET  /api/listings/popular/
// - POST /api/listings/by-url/
// - GET  /api/listings/{pk}/

export async function getPopular(limit) {
  const params = {};
  if (typeof limit === 'number') {
    params.limit = limit;
  }
  const response = await instance.get('/api/listings/popular/', { params });
  return response.data;
}

export async function getByUrl(url) {
  const response = await instance.post('/api/listings/by-url/', { url });
  return response.data;
}

export async function getDetail(id) {
  const response = await instance.get(`/api/listings/${id}/`);
  return response.data;
}
