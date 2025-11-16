<script setup>
import { ref, onMounted, computed } from 'vue';
import SolarTrashBin2Bold from '~icons/solar/trash-bin-2-bold';
import Popup from '@/components/Popup.vue';
import { authFetch } from '@/utils/auth';

const props = defineProps({
  electionId: [String, Number]
});

const showAddCandidatePopup = ref(false);
const newCandidateName = ref('');
const selectedPostId = ref(null);
const newImageFile = ref(null);
const popupError = ref('');
const fileInput = ref(null);

const postsWithCandidates = ref([]);
const loading = ref(false);
const error = ref('');

const totalCandidates = computed(() => {
  return postsWithCandidates.value.reduce((sum, p) => sum + (p.candidates ? p.candidates.length : 0), 0);
});

async function loadPostsWithCandidates() {
  loading.value = true;
  error.value = '';
  try {
    const resp = await authFetch(`/api/v1/elections/${props.electionId}/posts?include_candidates=true`);
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      error.value = json?.message || 'Failed to load posts and candidates';
      return;
    }
    postsWithCandidates.value = json?.data?.posts || [];
  } catch (err) {
    console.error(err);
    error.value = err?.message || 'Failed to load posts and candidates';
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  if (props.electionId) loadPostsWithCandidates();
});

const openAddCandidatePopup = (postId = null) => {
  selectedPostId.value = postId;
  popupError.value = '';
  showAddCandidatePopup.value = true;
};

const onFileChange = (e) => {
  const file = e.target.files && e.target.files[0]
  if (file) {
    // Revoke previous preview if any
    if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
    newImageFile.value = file
    previewUrl.value = URL.createObjectURL(file)
  }
}

const previewUrl = ref(null)

const clearSelectedImage = () => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
  previewUrl.value = null
  newImageFile.value = null
}

const triggerFileSelect = () => {
  if (fileInput.value) fileInput.value.click()
}

const addCandidate = async () => {
  // backend will assign wallet_address, so frontend only needs name, post, image
  if (!selectedPostId.value || !newCandidateName.value || !newImageFile.value) {
    popupError.value = 'Please provide a name, select a post, and choose an image.';
    return;
  }

  try {
    const form = new FormData();
    form.append('name', newCandidateName.value);
    form.append('election_id', props.electionId);
    form.append('post_id', selectedPostId.value);
    if (newImageFile.value) form.append('image', newImageFile.value);

    const resp = await authFetch('/api/v1/candidates', { method: 'POST', body: form });
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      // prefer backend validation messages
      popupError.value = json?.message || 'Failed to add candidate';
      return;
    }
    showAddCandidatePopup.value = false;
    newCandidateName.value = '';
    newImageFile.value = null;
    selectedPostId.value = null;
    popupError.value = '';
    await loadPostsWithCandidates();
  } catch (err) {
    console.error(err);
    popupError.value = err?.message || 'Failed to add candidate';
  }
};

const deleteCandidate = async (postId, candidateId) => {
  try {
    const resp = await authFetch(`/api/v1/candidates/${candidateId}`, { method: 'DELETE' });
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) throw new Error(json?.message || 'Failed to delete candidate');
    await loadPostsWithCandidates();
  } catch (err) {
    console.error(err);
    error.value = err?.message || 'Failed to delete candidate';
  }
};

const closeAddCandidatePopup = () => {
  showAddCandidatePopup.value = false;
  popupError.value = '';
  newCandidateName.value = '';
  clearSelectedImage();
  selectedPostId.value = null;
};
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold">Candidates by Post</h2>
      <div>
        <button @click="openAddCandidatePopup()" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg cursor-pointer transition-colors duration-300">Add Candidate</button>
      </div>
    </div>

    <div v-if="loading">Loading posts and candidates...</div>
    <div v-else-if="error" class="text-red-600">{{ error }}</div>
    <div v-else-if="!loading && totalCandidates === 0" class="p-4 text-neutral-600">There are no candidates for this election yet.</div>
    <div v-else>
      <div v-for="post in postsWithCandidates" :key="post.id" class="bg-white rounded-lg shadow-inner p-6 mb-6">
        <div class="flex justify-between items-center mb-4">
          <h3 class="text-xl font-semibold text-gray-800">{{ post.title }}</h3>
        </div>
        <ul v-if="post.candidates && post.candidates.length > 0">
          <li v-for="candidate in post.candidates" :key="candidate.id" class="flex items-center justify-between p-3 border-b border-gray-200 last:border-b-0">
            <div class="flex items-center">
              <img v-if="candidate.image_url" :src="candidate.image_url" alt="candidate" class="w-12 h-12 object-cover rounded mr-4" />
              <span class="text-lg text-gray-700">{{ candidate.name }}</span>
            </div>
            <button @click="deleteCandidate(post.id, candidate.id)" class="text-red-500 hover:text-red-700 cursor-pointer">
              <solar-trash-bin-2-bold class="h-6 w-6" />
            </button>
          </li>
        </ul>
        <p v-else class="text-gray-500">No candidates for this post yet.</p>
      </div>
    </div>

    <!-- Add Candidate Popup -->
    <Popup v-if="showAddCandidatePopup">
      <template #header>Add New Candidate</template>
      <template #body>
        <p class="text-sm text-gray-500 mb-4">Enter the name of the new candidate and select their post.</p>
        <input v-model="newCandidateName" type="text" class="w-full px-4 py-3 bg-gray-200 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 mb-4" placeholder="Enter candidate name">
        <select v-model="selectedPostId" class="w-full px-4 py-3 bg-gray-200 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 mb-4">
          <option value="" disabled>Select a Post</option>
          <option v-for="post in postsWithCandidates" :key="post.id" :value="post.id">{{ post.title }}</option>
        </select>
        <div class="mb-4">
            <label class="block text-sm text-gray-600 mb-2">Candidate Image <span class="text-red-500">(required)</span></label>
            <input ref="fileInput" type="file" accept="image/*" @change="onFileChange" class="hidden" />
            <div class="flex items-center gap-3">
              <button type="button" @click="triggerFileSelect" class="bg-white border border-gray-300 px-3 py-2 rounded-lg hover:bg-gray-50">Choose image</button>
              <div v-if="previewUrl" class="flex items-center gap-2">
                <img :src="previewUrl" alt="preview" class="w-12 h-12 object-cover rounded" />
                <div class="text-sm text-gray-700">{{ newImageFile ? newImageFile.name : '' }}</div>
                <button type="button" @click="clearSelectedImage" class="text-red-500 hover:text-red-700">Remove</button>
              </div>
              <div v-else class="text-sm text-neutral-500">No image selected (required)</div>
            </div>
          </div>
        <p v-if="popupError" class="text-red-600 text-sm mb-2">{{ popupError }}</p>
      </template>
      <template #footer>
  <button @click="addCandidate" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg mr-2 cursor-pointer transition-colors duration-300">Add</button>
  <button @click="closeAddCandidatePopup" class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-3 px-6 rounded-lg cursor-pointer transition-colors duration-300">Cancel</button>
      </template>
    </Popup>
  </div>
</template>
