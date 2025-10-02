<script setup>
import Navbar from '@/components/Navbar.vue';
import Sidebar from '@/components/Sidebar.vue';
import Breadcrumb from '@/components/Breadcrumb.vue';
import DetailsTab from '@/components/DetailsTab.vue';
import AdminsTab from '@/components/AdminsTab.vue';
import PostsTab from '@/components/PostsTab.vue';
import CandidatesTab from '@/components/CandidatesTab.vue';
import VotersTab from '@/components/VotersTab.vue';
import InstitutionalRecordsTab from '@/components/InstitutionalRecordsTab.vue';
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
        <div class="bg-white mt-5 p-8 rounded-2xl shadow-lg">
          <DetailsTab v-if="currentSection === 'Details'" />
          <AdminsTab v-else-if="currentSection === 'Admins'" />
          <PostsTab v-else-if="currentSection === 'Posts'" />
          <CandidatesTab v-else-if="currentSection === 'Candidates'" />
          <VotersTab v-else-if="currentSection === 'Voters'" />
          <InstitutionalRecordsTab v-else-if="currentSection === 'Institutional records'" />
          <div v-else>
            <h2 class="text-2xl font-bold text-blue-600 mb-6">Ops! This is an error that shouldnt be. Please contact the developer</h2>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>