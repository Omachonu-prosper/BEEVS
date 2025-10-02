<script setup>
import Navbar from '@/components/Navbar.vue';
import Sidebar from '@/components/Sidebar.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const electionId = route.params.id;

const crumbs = [
  { text: 'Dashboard', to: '/dashboard' },
  { text: electionId, to: '' }
];

</script>

<template>
  <div>
    <Navbar />
    <div class="flex">
      <Sidebar />
      <div class="flex-1 p-8 pt-10">
        <Breadcrumb :crumbs="crumbs" />
        <h1 class="text-2xl font-bold mb-4 mt-4">{{ electionId }}</h1>
        <div class="bg-white p-4 rounded-lg shadow-md">
          <h2 class="text-lg font-semibold mb-2">Election Data</h2>
          <p>Here is some placeholder data for the election.</p>
          <ul>
            <li><strong>Status:</strong> In Progress</li>
            <li><strong>Voter Turnout:</strong> 45%</li>
            <li><strong>Candidates:</strong> 5</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
