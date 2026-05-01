import axios from 'axios';

// Ekhane priority deya hoyeche env file ke, na thakle default 8000 use hobe
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        });
        const { access_token, refresh_token } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', refresh_token);
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  login: (data) => api.post('/auth/login', data),
  refresh: (refreshToken) => api.post('/auth/refresh', { refresh_token: refreshToken }),
  me: () => api.get('/auth/me'),
  farmerProfile: (data) => api.post('/auth/farmer-profile', data),
  buyerProfile: (data) => api.post('/auth/buyer-profile', data),
};

// Products API
export const productsAPI = {
  list: (params) => api.get('/products', { params }),
  get: (id) => api.get(`/products/${id}`),
  create: (data) => api.post('/products', data),
  update: (id, data) => api.put(`/products/${id}`, data),
  delete: (id) => api.delete(`/products/${id}`),
  myProducts: () => api.get('/products/my/products'),
};

// Upload API
export const uploadAPI = {
  image: (formData) => api.post('/upload/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
  images: (formData) => api.post('/upload/images', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  }),
};

// Orders API
export const ordersAPI = {
  create: (data) => api.post('/orders', data),
  list: (params) => api.get('/orders', { params }),
  my: () => api.get('/orders/my'),
  get: (id) => api.get(`/orders/${id}`),
  approve: (id, data) => api.patch(`/orders/${id}/approve`, data),
  reject: (id, data) => api.patch(`/orders/${id}/reject`, data),
  cancel: (id) => api.patch(`/orders/${id}/cancel`),
  incoming: () => api.get('/orders/incoming'),
};

// Payments API
export const paymentsAPI = {
  advance: (data) => api.post('/payments/advance', data),
  final: (data) => api.post('/payments/final', data),
  orderPayments: (orderId) => api.get(`/payments/order/${orderId}`),
  my: () => api.get('/payments/my'),
  calculate: (orderId) => api.get(`/payments/calculate/${orderId}`),
};

// Delivery API
export const deliveryAPI = {
  create: (data) => api.post('/deliveries', data),
  orderDelivery: (orderId) => api.get(`/deliveries/order/${orderId}`),
  updateStatus: (id, data) => api.patch(`/deliveries/${id}/status`, data),
  my: () => api.get('/deliveries/my'),
};

// Insurance Claims API
export const claimsAPI = {
  create: (data) => api.post('/claims', data),
  list: (params) => api.get('/claims', { params }),
  my: () => api.get('/claims/my'),
  get: (id) => api.get(`/claims/${id}`),
  review: (id, data) => api.patch(`/claims/${id}/review`, data),
  approve: (id, data) => api.patch(`/claims/${id}/approve`, data),
  reject: (id, data) => api.patch(`/claims/${id}/reject`, data),
};

// Dashboard API
export const dashboardAPI = {
  farmer: () => api.get('/dashboard/farmer'),
  buyer: () => api.get('/dashboard/buyer'),
  admin: () => api.get('/dashboard/admin'),
};

// Resolve image URL: if relative (/uploads/...), prepend backend host in production
export function resolveImageUrl(url) {
  if (!url) return '';
  if (/^https?:\/\//i.test(url)) return url;
  // VITE_API_URL is like "https://backend.onrender.com/api"; strip trailing /api to get host
  const apiUrl = import.meta.env.VITE_API_URL || '';
  if (apiUrl) {
    const host = apiUrl.replace(/\/api\/?$/, '');
    return `${host}${url.startsWith('/') ? '' : '/'}${url}`;
  }
  return url;
}

export default api;