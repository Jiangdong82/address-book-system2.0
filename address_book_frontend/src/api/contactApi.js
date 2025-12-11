import axios from 'axios';

const baseUrl = 'http://localhost:5000/api';

// 联系人相关
export const getContacts = (params) => axios.get(`${baseUrl}/contacts`, { params });
export const getContact = (id) => axios.get(`${baseUrl}/contacts/${id}`);
export const createContact = (data) => axios.post(`${baseUrl}/contacts`, data);
export const updateContact = (id, data) => axios.put(`${baseUrl}/contacts/${id}`, data);
export const toggleFavorite = (id) => axios.patch(`${baseUrl}/contacts/${id}/favorite`);
export const deleteContact = (id) => axios.delete(`${baseUrl}/contacts/${id}`);

// 导入导出
export const exportContacts = () => axios.get(`${baseUrl}/contacts/export`, {
    responseType: 'blob'  // 关键：否则后端返回的二进制数据会被解析为JSON，导致文件损坏
});
export const importContacts = (formData) => axios.post(`${baseUrl}/contacts/import`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
});

// 分组相关
export const getGroups = () => axios.get(`${baseUrl}/groups`);
export const createGroup = (data) => axios.post(`${baseUrl}/groups`, data);

// 分组更新和删除
export const updateGroup = (id, data) => axios.put(`${baseUrl}/groups/${id}`, data);
export const deleteGroup = (id) => axios.delete(`${baseUrl}/groups/${id}`);