<script setup>
import { ref } from 'vue';
import SolarTrashBin2Bold from '~icons/solar/trash-bin-2-bold';
import Popup from '@/components/Popup.vue';

const showAddPostPopup = ref(false);
const newPostTitle = ref('');
const showAddCandidatePopup = ref(false);
const newCandidateName = ref('');
const selectedPostId = ref(null);

const postsWithCandidates = ref([
  {
    id: 1,
    title: 'President',
    candidates: [
      { id: 101, name: 'Alice Smith' },
      { id: 102, name: 'Bob Johnson' },
    ],
  },
  {
    id: 2,
    title: 'Secretary',
    candidates: [
      { id: 201, name: 'Charlie Brown' },
    ],
  },
]);

const openAddCandidatePopup = (postId) => {
  selectedPostId.value = postId;
  showAddCandidatePopup.value = true;
};

const addCandidate = () => {
  if (newCandidateName.value.trim() !== '' && selectedPostId.value !== null) {
    const post = postsWithCandidates.value.find(p => p.id === selectedPostId.value);
    if (post) {
      post.candidates.push({ id: Date.now(), name: newCandidateName.value });
    }
    newCandidateName.value = '';
    showAddCandidatePopup.value = false;
    selectedPostId.value = null;
  }
};

const deleteCandidate = (postId, candidateId) => {
  const post = postsWithCandidates.value.find(p => p.id === postId);
  if (post) {
    post.candidates = post.candidates.filter(c => c.id !== candidateId);
  }
};
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-blue-600">Candidates by Post</h2>
      <div>
        <button @click="showAddCandidatePopup = true" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg cursor-pointer transition-colors duration-300">Add Candidate</button>
      </div>
    </div>

    <div v-for="post in postsWithCandidates" :key="post.id" class="bg-white rounded-lg shadow-inner p-6 mb-6">
      <div class="flex justify-between items-center mb-4">
        <h3 class="text-xl font-semibold text-gray-800">{{ post.title }}</h3>
      </div>
      <ul v-if="post.candidates.length > 0">
        <li v-for="candidate in post.candidates" :key="candidate.id" class="flex items-center justify-between p-3 border-b border-gray-200 last:border-b-0">
          <span class="text-lg text-gray-700">{{ candidate.name }}</span>
          <button @click="deleteCandidate(post.id, candidate.id)" class="text-red-500 hover:text-red-700 cursor-pointer">
            <solar-trash-bin-2-bold class="h-6 w-6" />
          </button>
        </li>
      </ul>
      <p v-else class="text-gray-500">No candidates for this post yet.</p>
    </div>

    <!-- Add Candidate Popup -->
    <Popup v-if="showAddCandidatePopup">
      <template #header>Add New Candidate</template>
      <template #body>
        <p class="text-sm text-gray-500 mb-4">Enter the name of the new candidate and select their post.</p>
        <input v-model="newCandidateName" type="text" class="w-full px-4 py-3 bg-gray-200 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 mb-4" placeholder="Enter candidate name">
        <select v-model="selectedPostId" class="w-full px-4 py-3 bg-gray-200 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600">
          <option value="" disabled>Select a Post</option>
          <option v-for="post in postsWithCandidates" :key="post.id" :value="post.id">{{ post.title }}</option>
        </select>
      </template>
      <template #footer>
        <button @click="addCandidate" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg mr-2 cursor-pointer transition-colors duration-300">Add</button>
        <button @click="showAddCandidatePopup = false" class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-3 px-6 rounded-lg cursor-pointer transition-colors duration-300">Cancel</button>
      </template>
    </Popup>
  </div>
</template>
