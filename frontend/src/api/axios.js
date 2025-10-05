import axios from "axios";

const api = axios.create({
  baseURL: "/",
  withCredentials: true,
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});
api.interceptors.request.use((config) => {
  const activeRole = localStorage.getItem("active_role"); // manager|service|client
  if (activeRole) {
    config.headers["X-Active-Role"] = activeRole;
  }
  return config;
});
export default api;
