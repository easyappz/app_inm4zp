import instance from './axios';

// Easyappz API: Comments layer strictly per api_schema.yaml/openapi.yml
// Listing comments
export async function list(listingId, opts = {}) {
  const params = {};
  if (typeof opts.limit === 'number') params.limit = opts.limit;
  if (typeof opts.offset === 'number') params.offset = opts.offset;
  const response = await instance.get(`/api/listings/${listingId}/comments/`, { params });
  return response.data;
}

export async function create(listingId, payload) {
  // payload: { content: string }
  const response = await instance.post(`/api/listings/${listingId}/comments/`, payload);
  return response.data;
}

// Comment detail
export async function get(pk) {
  const response = await instance.get(`/api/comments/${pk}/`);
  return response.data;
}

export async function update(pk, payload) {
  // payload: { content?: string }
  const response = await instance.patch(`/api/comments/${pk}/`, payload);
  return response.data;
}

export async function remove(pk) {
  const response = await instance.delete(`/api/comments/${pk}/`);
  return response.data;
}

export async function toggleLike(pk) {
  const response = await instance.post(`/api/comments/${pk}/like/`);
  return response.data;
}
