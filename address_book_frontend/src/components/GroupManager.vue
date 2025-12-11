<!-- src/components/GroupManager.vue -->
<template>
  <div class="group-manager card" style="max-width: 600px; margin: 0 auto;">
    <h2 class="title mb-20" style="color: #333; font-size: 18px;">分组管理</h2>

    <!-- 添加分组表单 -->
    <div class="add-group-form flex-gap mb-20">
      <input v-model="groupName" type="text" class="form-input flex-1" placeholder="请输入分组名称" />
      <button @click="createGroup" class="btn btn-primary">添加分组</button>
    </div>

    <!-- 分组列表 -->
    <div class="group-list">
      <div v-for="group in groups" :key="group.id" class="group-item flex-between mb-10 p-10 rounded">
        <span class="group-name">{{ group.name }}</span>
        <div class="group-actions flex-gap">
          <button @click="editGroup(group)" class="btn btn-secondary btn-sm">编辑</button>
          <button @click="deleteGroup(group.id)" class="btn btn-danger btn-sm">删除</button>
        </div>
      </div>
    </div>

    <!-- 空数据提示 -->
    <div v-if="groups.length === 0" class="empty-tip text-center py-20">
      <p style="color: var(--gray-color);">暂无分组数据，请添加分组~</p>
    </div>

    <!-- 编辑分组弹窗（简单实现） -->
    <div v-if="showEditModal" class="modal-mask" @click.self="closeModal">
      <div class="modal-content card" style="max-width: 400px; margin: 100px auto;">
        <h3 class="modal-title mb-20">编辑分组</h3>
        <input v-model="editGroupName" type="text" class="form-input mb-20" placeholder="请输入新的分组名称" />
        <div class="modal-actions flex-gap justify-end">
          <button @click="closeModal" class="btn btn-secondary">取消</button>
          <button @click="updateGroup" class="btn btn-primary">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getGroups, createGroup as apiCreateGroup, updateGroup as apiUpdateGroup, deleteGroup as apiDeleteGroup } from '../api/contactApi';

const groups = ref([]);
const groupName = ref('');
const showEditModal = ref(false);
const currentGroupId = ref('');
const editGroupName = ref('');

// 加载分组
const fetchGroups = async () => {
  const res = await getGroups();
  groups.value = res.data;
};

onMounted(() => {
  fetchGroups();
});

// 添加分组
const createGroup = async () => {
  if (!groupName.value.trim()) {
    alert('请输入分组名称！');
    return;
  }
  try {
    await apiCreateGroup({ name: groupName.value });
    alert('分组添加成功！');
    groupName.value = '';
    fetchGroups();
  } catch (error) {
    alert('添加失败：' + (error.response?.data?.error || '分组已存在'));
  }
};

// 编辑分组
const editGroup = (group) => {
  currentGroupId.value = group.id;
  editGroupName.value = group.name;
  showEditModal.value = true;
};

// 关闭弹窗
const closeModal = () => {
  showEditModal.value = false;
  editGroupName.value = '';
  currentGroupId.value = '';
};

// 更新分组
const updateGroup = async () => {
  if (!editGroupName.value.trim()) {
    alert('请输入分组名称！');
    return;
  }
  try {
    // 补充后端的更新分组接口（之前的代码中未实现，需添加）
    await apiUpdateGroup(currentGroupId.value, { name: editGroupName.value });
    alert('分组修改成功！');
    closeModal();
    fetchGroups();
  } catch (error) {
    alert('修改失败：' + (error.response?.data?.error || '分组已存在'));
  }
};

// 删除分组
const deleteGroup = async (id) => {
  if (confirm('确定删除该分组吗？分组下的联系人将变为无分组！')) {
    try {
      await apiDeleteGroup(id);
      fetchGroups();
    } catch (error) {
      alert('删除失败：' + error.response?.data?.error);
    }
  }
};
</script>

<style scoped>
/* 分组项样式 */
.group-item {
  background-color: #f8f9fa;
  border-radius: 4px;
  transition: background-color 0.2s ease;
}

.group-item:hover {
  background-color: #eef1f5;
}

.p-10 {
  padding: 10px;
}

.rounded {
  border-radius: 4px;
}

/* 弹窗样式 */
.modal-mask {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  padding: 20px;
}

.modal-title {
  font-size: 16px;
  color: #333;
}

.justify-end {
  justify-content: flex-end;
}

/* 输入框样式 */
.form-input {
  padding: 10px 12px;
  border-radius: 4px;
  border: 1px solid var(--gray-light);
  font-size: 14px;
}
</style>