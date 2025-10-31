import instance from './axios';

export const comments = {
  async list(listingId, { limit = 20, offset = 0 } = {}) {
    const { data } = await instance.get(`/api/listings/${listingId}/comments/`, { params: { limit, offset } });
    return data;
  },
  async create(listingId, content) {
    const { data } = await instance.post(`/api/listings/${listingId}/comments/`, { content });
    return data;
  },
  async update(id, payload) {
    const { data } = await instance.patch(`/api/comments/${id}/`, payload);
    return data;
  },
  async remove(id) {
    await instance.delete(`/api/comments/${id}/`);
    return true;
  },
  async toggleLike(id) {
    const { data } = await instance.post(`/api/comments/${id}/like/`);
    return data;
  },
};

export default comments;
