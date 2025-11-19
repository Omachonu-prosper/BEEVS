<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { authFetch } from '@/utils/auth';

const route = useRoute();
const router = useRouter();
const electionId = route.params.electionId;

const electionResults = ref([]);
const election = ref({});
const loading = ref(true);
const error = ref('');

const getWinner = (candidates) => {
  if (!candidates || candidates.length === 0) return 'N/A';
  const sortedCandidates = [...candidates].sort((a, b) => b.votes - a.votes);
  return sortedCandidates[0].name;
};

const getMaxVotes = (candidates) => {
  if (!candidates || candidates.length === 0) return 0;
  return Math.max(...candidates.map(c => c.votes));
};

const getBarWidth = (votes, maxVotes) => {
  if (maxVotes === 0) return '0%';
  return `${(votes / maxVotes) * 100}%`;
};

const getPercentage = (votes, totalVotes) => {
  if (totalVotes === 0) return '0';
  return ((votes / totalVotes) * 100).toFixed(1);
};

const getTotalVotes = (candidates) => {
  if (!candidates || candidates.length === 0) return 0;
  return candidates.reduce((sum, c) => sum + (c.votes || 0), 0);
};

async function loadResults() {
  loading.value = true;
  error.value = '';
  try {
    const resp = await authFetch(`/api/v1/elections/${electionId}/results`);
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      error.value = json?.message || 'Failed to load election results';
      return;
    }
    election.value = json?.data?.election || {};
    electionResults.value = json?.data?.results || [];
  } catch (err) {
    console.error(err);
    error.value = err?.message || 'Failed to load election results';
  } finally {
    loading.value = false;
  }
}

const goToAudit = () => {
  router.push(`/audit/${electionId}/auth`);
};

onMounted(() => {
  loadResults();
});
</script>

<template>
  <div class="min-h-screen bg-neutral-100 p-8">
    <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
      <h1 class="text-3xl font-bold text-blue-600 mb-2 text-center">Election Results</h1>
      <p v-if="election.title" class="text-xl text-gray-600 mb-8 text-center">{{ election.title }}</p>

      <div v-if="loading" class="text-center py-12">
        <div class="inline-block">
          <svg class="animate-spin h-12 w-12 text-blue-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
          </svg>
        </div>
        <p class="mt-4 text-gray-600">Loading results...</p>
      </div>

      <div v-else-if="error" class="text-center py-12">
        <p class="text-red-600 text-lg">{{ error }}</p>
      </div>

      <div v-else-if="electionResults.length === 0" class="text-center py-12">
        <p class="text-gray-600 text-lg">No results available yet.</p>
      </div>

      <div v-else>
        <div v-for="position in electionResults" :key="position.id" class="mb-10">
          <h2 class="text-2xl font-semibold text-gray-800 mb-6 border-b-2 border-blue-200 pb-2">{{ position.title }}</h2>
          
          <div v-if="position.candidates.length === 0" class="text-gray-500 italic mb-4">
            No candidates for this position.
          </div>
          
          <div v-else class="space-y-4">
            <div v-for="candidate in position.candidates" :key="candidate.id" class="flex items-center gap-4">
              <img v-if="candidate.image_url" :src="candidate.image_url" :alt="candidate.name" class="w-12 h-12 rounded-full object-cover flex-shrink-0" />
              <div v-else class="w-12 h-12 rounded-full bg-gray-300 flex-shrink-0 flex items-center justify-center text-gray-600 font-bold">
                {{ candidate.name.charAt(0) }}
              </div>
              <p class="w-1/5 text-lg font-medium text-gray-700">{{ candidate.name }}</p>
              <div class="flex-1 flex items-center gap-3">
                <div class="flex-1 bg-gray-200 rounded-full h-8 relative overflow-hidden">
                  <div 
                    :style="{ width: getBarWidth(candidate.votes, getMaxVotes(position.candidates)) }"
                    :class="[
                      'h-full rounded-full transition-all duration-500',
                      candidate.votes === getMaxVotes(position.candidates) && candidate.votes > 0 ? 'bg-green-500' : 'bg-blue-500'
                    ]"
                  ></div>
                </div>
                <div class="flex items-center gap-2 min-w-[120px]">
                  <span class="text-lg font-bold text-gray-800">{{ candidate.votes }}</span>
                  <span class="text-sm text-gray-600">({{ getPercentage(candidate.votes, getTotalVotes(position.candidates)) }}%)</span>
                </div>
              </div>
            </div>
          </div>
          
          <p v-if="position.winner" class="text-xl font-bold text-green-600 mt-6 text-center">
            Winner: {{ position.winner }}
          </p>
        </div>

        <!-- Audit Trail Link -->
        <div class="mt-12 pt-8 border-t border-gray-200">
          <div class="bg-blue-50 rounded-lg p-6 text-center">
            <h3 class="text-lg font-semibold text-gray-800 mb-2">Verify Your Vote</h3>
            <p class="text-sm text-gray-600 mb-4">
              Did you vote in this election? View your voting audit trail and verify your votes on the blockchain.
            </p>
            <button
              @click="goToAudit"
              class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-300 inline-flex items-center gap-2"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.012 4.536A9 9 0 1118 3.52"></path>
              </svg>
              Audit My Vote
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
