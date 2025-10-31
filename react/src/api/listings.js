import instance from './axios';

export const listings = {
  async getPopular(limit = 20) {
    const { data } = await instance.get('/api/listings/popular/', { params: { limit } });
    return data;
  },
  async getByUrl(url) {
    const { data } = await instance.post('/api/listings/by-url/', { url });
    return data;
  },
  async getDetail(id) {
    const { data } = await instance.get(`/api/listings/${id}/`);
    return data;
  },
};

export default listings;
