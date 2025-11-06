import axios from "axios";
import apiConfig from "./api";
import mitt from "mitt";

export const modalEventEmitter = mitt();

const api = axios.create({
  baseURL: apiConfig.BASE_URL,
});

const errorHandler = (error: any) => {
  const statusCode = error.response?.status;

  if (statusCode && statusCode !== 401) {
    console.error(error);
  }

  return Promise.reject(error);
};

api.interceptors.response.use(undefined, (error) => {
  return errorHandler(error);
});

export default api;
