import axios from "axios";
const client = axios.create({
  baseURL: "https://heritage-trace-2.onrender.com/api",
});
export default client;