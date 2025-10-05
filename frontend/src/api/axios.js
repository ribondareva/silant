import axios from "axios";

const api = axios.create({
  baseURL: "/",
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

api.interceptors.request.use((config) => {
  const access = localStorage.getItem("access");
  if (access) config.headers["Authorization"] = `Bearer ${access}`;

  const activeRole = localStorage.getItem("active_role");
  if (activeRole) config.headers["X-Active-Role"] = activeRole;

  return config;
});

api.interceptors.response.use(
  (r) => r,
  async (err) => {
    const original = err.config;
    if (err.response?.status === 401 && !original._retry) {
      const refresh = localStorage.getItem("refresh");
      if (!refresh) throw err;
      original._retry = true;
      const { data } = await axios.post("/api/auth/jwt/refresh/", { refresh });
      localStorage.setItem("access", data.access);
      original.headers["Authorization"] = `Bearer ${data.access}`;
      return api(original);
    }
    throw err;
  }
);

export default api;
