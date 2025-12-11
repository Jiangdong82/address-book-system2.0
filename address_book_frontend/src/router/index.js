import { createRouter, createWebHistory } from 'vue-router';
import ContactList from '../components/ContactList.vue';
import ContactForm from '../components/ContactForm.vue';
import GroupManager from '../components/GroupManager.vue';

const routes = [
  { path: '/', component: ContactList },
  { path: '/add-contact', component: ContactForm },
  { path: '/edit-contact/:id', component: ContactForm },
  { path: '/groups', component: GroupManager }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;