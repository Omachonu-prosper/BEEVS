<script setup>
import Navbar from '@/components/Navbar.vue';
import Sidebar from '@/components/Sidebar.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import Popup from '@/components/Popup.vue';
import { useRoute } from 'vue-router';
import { ref } from 'vue';
import SolarTrashBin2Bold from '~icons/solar/trash-bin-2-bold';

const route = useRoute();
const electionId = route.params.id;
const currentSection = ref('Details');
const showAddAdminPopup = ref(false);
const adminEmails = ref('');

const admins = ref([
  { id: 1, name: 'John Doe' },
  { id: 2, name: 'Jane Smith' },
]);

const crumbs = [
  { text: 'Dashboard', to: '/dashboard' },
  { text: electionId, to: '' }
];

const handleSectionChange = (section) => {
  currentSection.value = section;
};

const addAdmins = () => {
  // Logic to add admins from comma-separated list
  console.log(adminEmails.value.split(',').map(email => email.trim()));
  showAddAdminPopup.value = false;
  adminEmails.value = '';
};

</script>

<template>
  <div>
    <Navbar />
    <div class="flex">
      <Sidebar :currentSection="currentSection" @section-change="handleSectionChange" />
      <div class="flex-1 p-8 pt-10">
        <Breadcrumb :crumbs="crumbs" />
        <h1 class="text-2xl font-bold mb-4 mt-4">{{ electionId }}</h1>
        <div class="bg-white p-4 rounded-lg shadow-md">
          <div v-if="currentSection === 'Details'">
            <h2 class="text-lg font-semibold mb-2">Election Data</h2>
            <p>Here is some placeholder data for the election.</p>
            <ul>
              <li><strong>Status:</strong> In Progress</li>
              <li><strong>Voter Turnout:</strong> 45%</li>
              <li><strong>Candidates:</strong> 5</li>
            </ul>
          </div>
          <div v-else-if="currentSection === 'Admins'">
            <div class="flex justify-between items-center mb-4">
              <h2 class="text-lg font-semibold">Active admins</h2>
              <button @click="showAddAdminPopup = true" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded cursor-pointer">Add Admin</button>
            </div>
            <ul>
              <li v-for="admin in admins" :key="admin.id" class="flex items-center justify-between p-2 border-b">
                <span>{{ admin.name }}</span>
                <button class="text-red-500 hover:text-red-700">
                  <solar-trash-bin-2-bold />
                </button>
              </li>
            </ul>
          </div>
          <div v-else>
            <h2 class="text-lg font-semibold mb-2">This is the {{ currentSection }} section</h2>
          </div>
        </div>
      </div>
    </div>
    <Popup v-if="showAddAdminPopup">
      <template #header>Add New Admins</template>
      <template #body>
        <p class="text-sm text-gray-500 mb-4">Enter the email addresses of the admins you want to add, separated by commas.</p>
        <input v-model="adminEmails" type="text" class="w-full p-2 border rounded" placeholder="Enter emails separated by commas">
      </template>
      <template #footer>
        <button @click="addAdmins" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded mr-2">Add</button>
        <button @click="showAddAdminPopup = false" class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded">Cancel</button>
      </template>
    </Popup>
  </div>
</template>
