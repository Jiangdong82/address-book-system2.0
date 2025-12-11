import axios from 'axios';

// 配置后端API基础地址
const api = axios.create({
    baseURL: 'http://localhost:5000/api',
    headers: {
        'Content-Type': 'application/json'
    }
});

export default api;