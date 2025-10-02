<script setup>
import { ref } from 'vue';
import SolarTrashBin2Bold from '~icons/solar/trash-bin-2-bold';
import Popup from '@/components/Popup.vue';

const showAddAdminPopup = ref(false);
const adminEmails = ref('');

const admins = ref([
  { id: 1, name: 'John Doe' },
  { id: 2, name: 'Jane Smith' },
]);

const addAdmins = () => {
  // Logic to add admins from comma-separated list
  console.log(adminEmails.value.split(',').map(email => email.trim()));
  showAddAdminPopup.value = false;
  adminEmails.value = '';
};
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-primary">Active admins</h2>
      <button @click="showAddAdminPopup = true" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg cursor-pointer transition-colors duration-300">Add Admin</button>
    </div>
    <ul class="bg-white rounded-lg shadow-inner">
      <li v-for="admin in admins" :key="admin.id" class="flex items-center justify-between p-4 border-b border-neutral-200 last:border-b-0">
        <span class="text-lg text-neutral-700">{{ admin.name }}</span>
        <button class="text-red-500 hover:text-red-700 cursor-pointer">
          <solar-trash-bin-2-bold class="h-6 w-6" />
        </button>
      </li>
    </ul>
    <Popup v-if="showAddAdminPopup">
      <template #header>Add New Admins</template>
      <template #body>
        <p class="text-sm text-neutral-500 mb-4">Enter the email addresses of the admins you want to add, separated by commas.</p>
        <input v-model="adminEmails" type="text" class="w-full px-4 py-3 bg-neutral-200 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600" placeholder="Enter emails separated by commas">
      </template>
      <template #footer>
        <button @click="addAdmins" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg mr-2 cursor-pointer transition-colors duration-300">Add</button>
        <button @click="showAddAdminPopup = false" class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-3 px-6 rounded-lg cursor-pointer transition-colors duration-300">Cancel</button>
      </template>
    </Popup>
  </div>
</template>
