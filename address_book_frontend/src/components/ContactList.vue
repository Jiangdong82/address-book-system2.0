<!-- src/components/ContactList.vue -->
<template>
  <div class="contact-list card">
    <!-- 头部筛选和操作区 -->
    <div class="header-actions flex-between mb-20">
      <h2 class="title" style="color: #333;">联系人列表</h2>
      <div class="actions flex-gap">
        <!-- 分组筛选 -->
        <select v-model="selectedGroup" @change="fetchContacts" class="form-select">
          <option value="">所有分组</option>
          <option v-for="group in groups" :key="group.id" :value="group.id">
            {{ group.name }}
          </option>
        </select>
        <!-- 收藏筛选 -->
        <button @click="showFavorite = !showFavorite" class="btn btn-secondary">
          {{ showFavorite ? '显示全部' : '显示收藏' }}
        </button>
        <!-- 导入导出 -->
        <input type="file" ref="fileInput" accept=".xlsx,.xls" @change="handleImport" style="display: none" />
        <button @click="$refs.fileInput.click()" class="btn btn-secondary">导入Excel</button>
        <button @click="handleExport" class="btn btn-secondary">导出Excel</button>
      </div>
    </div>

    <!-- 联系人列表表格 -->
    <div class="table-container" style="overflow-x: auto;">
      <table class="contact-table">
        <thead>
          <tr>
            <th>姓名</th>
            <th>分组</th>
            <th>联系方式</th>
            <th>收藏</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="contact in contacts" :key="contact.id" class="contact-row">
            <td>{{ contact.name }}</td>
            <td>{{ contact.group?.name || '无' }}</td>
            <td>
              <div v-for="info in contact.contact_infos" :key="info.id" class="info-item mb-10">
                <span class="info-type">{{ info.info_type }}：</span>
                <span>{{ info.info_value }}</span>
              </div>
            </td>
            <td>
              <button @click="handleFavorite(contact.id)" class="favorite-btn" :class="{ active: contact.is_favorite }">
                {{ contact.is_favorite ? '★' : '☆' }}
              </button>
            </td>
            <td class="action-buttons flex-gap">
              <router-link :to="`/edit-contact/${contact.id}`" class="btn btn-secondary btn-sm">编辑</router-link>
              <button @click="handleDelete(contact.id)" class="btn btn-danger btn-sm">删除</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 空数据提示 -->
    <div v-if="contacts.length === 0" class="empty-tip text-center py-40">
      <p style="color: var(--gray-color);">暂无联系人数据，请添加联系人~</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { getContacts, getGroups, toggleFavorite, exportContacts, importContacts, deleteContact } from '../api/contactApi';

const router = useRouter();
const contacts = ref([]);
const groups = ref([]);
const selectedGroup = ref('');
const showFavorite = ref(false);

// 加载分组和联系人
const fetchGroups = async () => {
  const res = await getGroups();
  groups.value = res.data;
};

const fetchContacts = async () => {
  const params = {
    group_id: selectedGroup.value,
    is_favorite: showFavorite.value ? 'true' : undefined
  };
  const res = await getContacts(params);
  contacts.value = res.data;
};

onMounted(() => {
  fetchGroups();
  fetchContacts();
});

// 监听收藏状态变化
watch(showFavorite, fetchContacts);

// 切换收藏
const handleFavorite = async (id) => {
  const res = await toggleFavorite(id);
  const contact = contacts.value.find(item => item.id === id);
  if (contact) {
    contact.is_favorite = res.data.is_favorite;
  }
};

// 导出Excel（优化后）
const handleExport = async () => {
  try {
    const res = await exportContacts();
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([res.data]));
    const link = document.createElement('a');
    link.href = url;
    // 从响应头中获取文件名（如果后端返回），否则使用默认名
    const contentDisposition = res.headers['content-disposition'];
    let fileName = '通讯录导出.xlsx';
    if (contentDisposition) {
      const matches = /filename\*=UTF-8''(.*)/.exec(contentDisposition);
      if (matches && matches[1]) {
        fileName = decodeURIComponent(matches[1]);
      }
    }
    link.download = fileName;
    link.click();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    alert('导出失败：' + (error.message || '服务器错误'));
  }
};

// 导入Excel
const handleImport = async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append('file', file);
  const res = await importContacts(formData);
  alert(res.data.message);
  fetchContacts();
  e.target.value = '';
};

// 删除联系人（修复后）
const handleDelete = async (id) => {
  if (confirm('确定删除该联系人吗？删除后将无法恢复！')) {
    try {
      await deleteContact(id);
      alert('联系人删除成功！');
      fetchContacts(); // 重新加载列表
    } catch (error) {
      alert('删除失败：' + (error.response?.data?.error || error.message));
    }
  }
};
</script>

<style scoped>
/* 表格样式 */
.contact-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.contact-table th {
  background-color: #f8f9fa;
  padding: 12px 15px;
  text-align: left;
  font-weight: 600;
  color: #666;
  border-bottom: 2px solid var(--gray-light);
}

.contact-table td {
  padding: 15px;
  border-bottom: 1px solid var(--gray-light);
  vertical-align: top;
}

/* 行hover效果 */
.contact-row:hover {
  background-color: #fafafa;
}

/* 联系方式样式 */
.info-type {
  font-weight: 600;
  color: var(--primary-color);
  margin-right: 5px;
}

/* 收藏按钮 */
.favorite-btn {
  background: none;
  font-size: 20px;
  color: var(--gray-color);
}

.favorite-btn.active {
  color: var(--warning-color);
  transform: scale(1.1);
}

/* 小按钮样式 */
.btn-sm {
  padding: 4px 10px;
  font-size: 12px;
}

/* 空数据提示 */
.py-40 {
  padding: 40px 0;
}

/* 筛选下拉框 */
.form-select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid var(--gray-light);
  font-size: 14px;
}
</style>