<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import SolarUserBold from '~icons/solar/user-bold';
import { authFetch } from '@/utils/auth';

const route = useRoute();
const router = useRouter();
const electionId = route.params.electionId;
const electionTitle = ref('');
const loadingPositions = ref(false);
const positionsError = ref('');

const positions = ref([]); // will be loaded from backend

const loadPositions = async () => {
  if (!electionId) return;
  loadingPositions.value = true;
  positionsError.value = '';
  try {
    const resp = await authFetch(`/api/v1/elections/${electionId}/posts?include_candidates=true`);
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      console.error('Failed to load posts', json);
      positions.value = [];
      positionsError.value = json?.message || 'Failed to load positions';
      return;
    }
    // map posts -> positions structure with selected flags
    positions.value = (json?.data?.posts || []).map((p) => ({
      id: p.id,
      title: p.title,
      candidates: (p.candidates || []).map((c) => ({ ...c, selected: false })),
    }));
  } catch (err) {
    console.error('Error loading posts', err);
    positions.value = [];
    positionsError.value = 'Error loading positions';
  }
  finally {
    loadingPositions.value = false;
  }
};

const loadElectionTitle = async () => {
  if (!electionId) return;
  try {
    const resp = await authFetch('/api/v1/elections');
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      console.error('Failed to load elections', json);
      electionTitle.value = `Election ${electionId}`;
      return;
    }
    const elections = json?.data?.elections || [];
    const found = elections.find((e) => String(e.id) === String(electionId));
    electionTitle.value = found ? found.title : `Election ${electionId}`;
  } catch (err) {
    console.error('Error loading election title', err);
    electionTitle.value = `Election ${electionId}`;
  }
};

onMounted(async () => {
  // Require prior voter authentication (vote token) before allowing access to the voting UI
  try {
    const voteToken = sessionStorage.getItem('vote_token');
    if (!voteToken) {
      // redirect to auth page
      router.replace(`/vote/${electionId}/auth`);
      return;
    }
  } catch (e) {
    // if sessionStorage is unavailable, still redirect to auth page
    router.replace(`/vote/${electionId}/auth`);
    return;
  }
  await loadElectionTitle();
  await loadPositions();
});

const selectCandidate = (positionId, candidateId) => {
  const position = positions.value.find(p => p.id === positionId);
  if (position) {
    position.candidates.forEach(c => (c.selected = false)); // Deselect all in this position
    const candidate = position.candidates.find(c => c.id === candidateId);
    if (candidate) candidate.selected = true;
  }
};

const showConfirm = ref(false);
const confirmList = ref([]);
const confirmLoading = ref(false);
const voteError = ref('');
const voteInfo = ref('');

const openConfirmation = () => {
  const selectedVotes = positions.value.map(position => ({
    positionId: position.id,
    positionTitle: position.title,
    selectedCandidate: position.candidates.find(c => c.selected),
  }));
  const missing = selectedVotes.filter(sv => !sv.selectedCandidate);
  if (missing.length > 0) {
    alert('Please select a candidate for every position before submitting.');
    return;
  }
  confirmList.value = selectedVotes;
  showConfirm.value = true;
};

const cancelConfirmation = () => {
  showConfirm.value = false;
  confirmList.value = [];
};

const confirmVotes = async () => {
  if (!confirmList.value || confirmList.value.length === 0) return;
  confirmLoading.value = true;
  try {
    // Build payload with selected candidate ids
    const payload = { votes: confirmList.value.map(item => ({ selectedCandidate: { id: item.selectedCandidate.id } })) };

    // Use vote token from sessionStorage (set by auth step)
    const voteToken = sessionStorage.getItem('vote_token');
    if (!voteToken) {
      alert('Missing voting token; please authenticate again.');
      router.replace(`/vote/${electionId}/auth`);
      return;
    }

    const resp = await authFetch(`/api/v1/elections/${electionId}/vote`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload), authToken: voteToken });
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      console.error('Vote submission failed', json);
      voteError.value = json?.message || 'Failed to submit votes';
      return;
    }

    // Success: show info, clear token and redirect to auth page for next voter
    voteInfo.value = json?.message || 'Votes submitted successfully';
    try { sessionStorage.removeItem('vote_token'); } catch (e) {}
    // give user a short moment to see the message, then redirect
    setTimeout(() => {
      router.replace(`/vote/${electionId}/auth`);
    }, 800);
  } catch (err) {
    console.error(err);
    alert(err?.message || 'Failed to submit votes');
  } finally {
    confirmLoading.value = false;
    showConfirm.value = false;
    confirmList.value = [];
  }
};
</script>

<template>
  <div class="min-h-screen bg-neutral-100 p-8">
    <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
  <h1 class="text-3xl font-bold text-blue-600 mb-8 text-center">Cast Your Vote for {{ electionTitle || electionId }}</h1>

  <div v-if="loadingPositions" class="text-center py-8">Loading positions...</div>
  <div v-else-if="positionsError" class="text-center text-red-600 py-8">{{ positionsError }}</div>
  <div v-else-if="voteError" class="text-center text-red-600 py-4">{{ voteError }}</div>
  <div v-else-if="voteInfo" class="text-center text-green-600 py-4">{{ voteInfo }}</div>
  <div v-else-if="positions.length === 0" class="text-center text-neutral-600 py-8">No positions found for this election.</div>
  <div v-else v-for="position in positions" :key="position.id" class="mb-10">
        <h2 class="text-2xl font-semibold text-gray-800 mb-6 border-b-2 border-blue-200 pb-2">{{ position.title }}</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          <div
            v-for="candidate in position.candidates" :key="candidate.id"
            @click="selectCandidate(position.id, candidate.id)"
            :class="[
              'bg-gray-100 p-8 rounded-lg shadow-md cursor-pointer transition-all duration-200',
              candidate.selected ? 'border-2 border-blue-600 ring-2 ring-blue-300' : 'hover:shadow-lg hover:border-blue-300 border-2 border-transparent'
            ]"
          >
            <div class="flex flex-col items-center">
              <img v-if="candidate.image_url" :src="candidate.image_url" class="h-24 w-24 md:h-32 md:w-32 rounded-full object-cover mb-4" />
              <SolarUserBold v-else class="h-24 w-24 md:h-32 md:w-32 text-gray-500 mb-4" />
              <p class="text-xl font-medium text-gray-700 text-center">{{ candidate.name }}</p>
            </div>
          </div>
        </div>
        <p v-if="position.candidates.some(c => c.selected)" class="mt-4 text-lg text-blue-600 font-semibold text-center">
          Selected: {{ position.candidates.find(c => c.selected).name }}
        </p>
      </div>

      <div class="mt-10 text-center">
        <button
          @click="openConfirmation"
          class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg cursor-pointer transition-colors duration-300 text-xl"
        >
          Submit Votes
        </button>
      </div>
      
      <!-- Confirmation modal -->
      <div v-if="showConfirm" class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
        <div class="bg-white rounded-lg shadow-lg w-11/12 max-w-2xl p-6">
          <h3 class="text-xl font-semibold mb-4">Please confirm that you want to vote</h3>
          <p class="text-sm text-neutral-600 mb-4">Review the posts and selected candidates below. Click Confirm to submit your vote.</p>
          <div class="space-y-3 max-h-64 overflow-auto mb-4">
            <div v-for="item in confirmList" :key="item.positionId" class="p-3 border rounded">
              <div class="flex items-center justify-between">
                <div class="font-medium">{{ item.positionTitle }}</div>
                <div class="text-neutral-700">{{ item.selectedCandidate?.name }}</div>
              </div>
            </div>
          </div>
          <div class="flex justify-end gap-3">
            <button @click="cancelConfirmation" :disabled="confirmLoading" class="px-4 py-2 rounded border">Cancel</button>
            <button @click="confirmVotes" :disabled="confirmLoading" class="px-4 py-2 rounded bg-blue-600 text-white inline-flex items-center">
              <svg v-if="confirmLoading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
              </svg>
              <span v-if="!confirmLoading">Confirm</span>
              <span v-else>Submitting...</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
