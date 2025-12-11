<!-- src/App.vue -->
<template>
  <div class="app-container">
    <!-- 导航栏（原有样式保留） -->
    <header class="navbar">
      <div class="container flex-between">
        <h1 class="logo gradient-text">📖 通讯录管理系统</h1> <!-- 新增渐变文字 -->
        <nav class="nav-menu flex-gap">
          <router-link to="/" class="nav-item" :class="{ active: $route.path === '/' }">联系人列表</router-link>
          <router-link to="/groups" class="nav-item" :class="{ active: $route.path === '/groups' }">分组管理</router-link>
          <router-link to="/add-contact" class="nav-item btn gradient-btn">添加联系人</router-link> <!-- 替换为渐变按钮 -->
        </nav>
      </div>
    </header>

    <!-- 路由出口：添加过渡动画 -->
    <main class="main-content container">
      <transition name="fade">
        <router-view />
      </transition>
    </main>

    <!-- 页脚（原有样式保留） -->
    <footer class="footer text-center">
      <p>© 2025 通讯录管理系统 | 设计与开发</p>
    </footer>
  </div>
</template>

<script setup>
// 引入全局样式
import './styles/global.css';
</script>

<style scoped>
/* 导航栏样式 */
.navbar {
  background-color: var(--white-color);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
  padding: 15px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.logo {
  font-size: 20px;
  color: var(--primary-color);
  font-weight: 600;
}

.nav-menu {
  font-size: 14px;
}

.nav-item {
  padding: 8px 15px;
  border-radius: 4px;
  transition: all 0.2s ease;
}

.nav-item:hover {
  color: var(--primary-color);
}

.nav-item.active {
  background-color: var(--primary-color);
  color: var(--white-color);
}

/* 主内容区 */
.main-content {
  padding: 30px 0;
  min-height: calc(100vh - 120px);
}

/* 页脚样式 */
.footer {
  padding: 20px 0;
  background-color: var(--white-color);
  color: var(--gray-color);
  font-size: 12px;
  border-top: 1px solid var(--gray-light);
}
</style>