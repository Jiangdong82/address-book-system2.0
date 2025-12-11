<!-- src/components/ContactForm.vue -->
<template>
  <div class="contact-form card" style="max-width: 800px; margin: 0 auto;">
    <h2 class="form-title mb-20" style="color: #333; font-size: 18px;">{{ isEdit ? '编辑联系人' : '添加新联系人' }}</h2>
    <form @submit.prevent="handleSubmit" class="form-content">
      <!-- 基础信息 -->
      <div class="form-group mb-20">
        <label class="form-label mb-10">姓名 <span class="required">*</span></label>
        <input v-model="form.name" type="text" class="form-input" required placeholder="请输入联系人姓名" />
      </div>

      <div class="form-row flex-gap mb-20">
        <div class="form-group flex-1">
          <label class="form-label mb-10">分组</label>
          <select v-model="form.group_id" class="form-input">
            <option value="">无分组</option>
            <option v-for="group in groups" :key="group.id" :value="group.id">
              {{ group.name }}
            </option>
          </select>
        </div>

        <div class="form-group flex-1">
          <label class="form-label mb-10">收藏</label>
          <div class="flex-gap align-center">
            <input v-model="form.is_favorite" type="checkbox" id="favorite" class="form-checkbox" />
            <label for="favorite">加入收藏夹</label>
          </div>
        </div>
      </div>

      <!-- 多联系方式 -->
      <div class="form-group mb-20">
        <label class="form-label mb-10">联系方式 <span class="required">*</span></label>
        <div v-for="(info, index) in form.contact_infos" :key="index" class="info-row flex-gap mb-10">
          <select v-model="info.info_type" class="form-input flex-1">
            <option value="电话">电话</option>
            <option value="邮箱">邮箱</option>
            <option value="微信">微信</option>
            <option value="QQ">QQ</option>
            <option value="地址">具体住址</option>
            <option value="小红书">小红书</option>
            <option value="抖音">抖音</option>
            <option value="其他">其他</option>
          </select>
          <input v-model="info.info_value" type="text" class="form-input flex-2" placeholder="请输入联系方式内容" />
          <button type="button" @click="removeInfo(index)" class="btn btn-danger btn-sm" v-if="form.contact_infos.length > 1">删除</button>
        </div>
        <button type="button" @click="addInfo" class="btn btn-secondary">+ 添加更多联系方式</button>
      </div>

      <!-- 提交按钮组 -->
      <div class="form-actions flex-gap">
        <button type="submit" class="btn btn-primary">保存</button>
        <button type="button" @click="$router.push('/')" class="btn btn-secondary">取消</button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { getGroups, createContact, getContact, updateContact } from '../api/contactApi';

const router = useRouter();
const route = useRoute();
const isEdit = ref(!!route.params.id);
const groups = ref([]);
const form = ref({
  name: '',
  group_id: '',
  is_favorite: false,
  contact_infos: [{ info_type: '电话', info_value: '' }]
});

// 加载分组
const fetchGroups = async () => {
  const res = await getGroups();
  groups.value = res.data;
};

// 加载编辑的联系人数据
const fetchContact = async () => {
  const res = await getContact(route.params.id);
  form.value = {
    name: res.data.name,
    group_id: res.data.group_id || '',
    is_favorite: res.data.is_favorite,
    contact_infos: res.data.contact_infos.length ? res.data.contact_infos : [{ info_type: '电话', info_value: '' }]
  };
};

onMounted(() => {
  fetchGroups();
  if (isEdit.value) {
    fetchContact();
  }
});

// 添加联系方式
const addInfo = () => {
  form.value.contact_infos.push({ info_type: '电话', info_value: '' });
};

// 移除联系方式
const removeInfo = (index) => {
  form.value.contact_infos.splice(index, 1);
};

// 提交表单
const handleSubmit = async () => {
  // 过滤空的联系方式
  form.value.contact_infos = form.value.contact_infos.filter(
    info => info.info_type && info.info_value.trim()
  );

  // 验证至少有一个联系方式
  if (form.value.contact_infos.length === 0) {
    alert('请至少添加一个联系方式！');
    return;
  }

  try {
    if (isEdit.value) {
      await updateContact(route.params.id, form.value);
    } else {
      await createContact(form.value);
    }
    alert(isEdit.value ? '联系人修改成功！' : '联系人添加成功！');
    router.push('/');
  } catch (error) {
    alert('操作失败：' + (error.response?.data?.error || '服务器错误'));
  }
};
</script>

<style scoped>
/* 表单样式 */
.form-content {
  font-size: 14px;
}

.form-label {
  display: block;
  color: #666;
  font-weight: 500;
}

.form-input {
  width: 100%;
  padding: 10px 12px;
  border-radius: 4px;
  border: 1px solid var(--gray-light);
  font-size: 14px;
}

.form-row {
  display: flex;
  gap: 20px;
}

.flex-1 {
  flex: 1;
}

.flex-2 {
  flex: 2;
}

.align-center {
  align-items: center;
}

/* 必选标记 */
.required {
  color: var(--danger-color);
}

/* 联系方式行 */
.info-row {
  align-items: center;
}

/* 复选框样式 */
.form-checkbox {
  width: 16px;
  height: 16px;
  margin-right: 5px;
}

/* 按钮组 */
.form-actions {
  margin-top: 30px;
}
</style>