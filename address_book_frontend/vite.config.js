import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src') // 配置别名，方便路径导入
    }
  },
  server: {
    port: 5173, // 前端服务端口
    proxy: {
      // 配置接口代理，解决跨域问题（后端地址）
      '/api': {
        target: 'http://127.0.0.1:5000', // 后端Flask服务地址
        changeOrigin: true,
        secure: false
      }
    }
  }
});