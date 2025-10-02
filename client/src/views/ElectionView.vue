<script setup>
import Navbar from '@/components/Navbar.vue';
import Sidebar from '@/components/Sidebar.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import DetailsTab from '@/components/DetailsTab.vue';
import AdminsTab from '@/components/AdminsTab.vue';
import PostsTab from '@/components/PostsTab.vue';
import { useRoute } from 'vue-router';
import { ref } from 'vue';

const route = useRoute();
const electionId = route.params.id;
const currentSection = ref('Details');

const crumbs = [
  { text: 'Dashboard', to: '/dashboard' },
  { text: electionId, to: '' }
];

const handleSectionChange = (section) => {
  currentSection.value = section;
};

</script>

<template>
  <div class="bg-neutral-100 min-h-screen">
    <Navbar />
    <div class="flex">
      <Sidebar :currentSection="currentSection" @section-change="handleSectionChange" />
      <div class="flex-1 p-8">
        <Breadcrumb :crumbs="crumbs" />
        <h1 class="text-3xl font-bold text-primary mb-8 mt-4">{{ electionId }}</h1>
        <div class="bg-white p-8 rounded-2xl shadow-lg">
          <DetailsTab v-if="currentSection === 'Details'" />
          <AdminsTab v-else-if="currentSection === 'Admins'" />
          <PostsTab v-else-if="currentSection === 'Posts'" />
          <div v-else>
            <h2 class="text-2xl font-bold text-primary mb-6">This is the {{ currentSection }} section</h2>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
