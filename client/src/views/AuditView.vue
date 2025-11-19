<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { authFetch } from '@/utils/auth';
import SolarUserBold from '~icons/solar/user-bold';
import SolarLinkBold from '~icons/solar/link-bold';

const route = useRoute();
const router = useRouter();
const electionId = route.params.electionId;

const loading = ref(true);
const errorMessage = ref('');
const auditData = ref(null);
const voter = ref(null);
const election = ref(null);
const votes = ref([]);

// Get etherscan base URL from environment or use default
const etherscanBaseUrl = computed(() => {
  return 'https://sepolia.etherscan.io';
});

const getEtherscanLink = (txHash) => {
  if (!txHash) return null;
  return `${etherscanBaseUrl.value}/tx/${txHash}`;
};

const loadAuditData = async () => {
  loading.value = true;
  errorMessage.value = '';

  try {
    const auditToken = sessionStorage.getItem('audit_token');
    if (!auditToken) {
      router.replace(`/audit/${electionId}/auth`);
      return;
    }

    const resp = await authFetch(`/api/v1/elections/${electionId}/audit`, {
      authToken: auditToken
    });

    const json = await resp.json().catch(() => ({}));

    if (!resp.ok) {
      errorMessage.value = json?.message || 'Failed to load audit data';
      loading.value = false;
      return;
    }

    auditData.value = json?.data;
    voter.value = json?.data?.voter;
    election.value = json?.data?.election;
    votes.value = json?.data?.votes || [];
  } catch (err) {
    console.error('Error loading audit data', err);
    errorMessage.value = err?.message || 'An error occurred while loading audit data';
  } finally {
    loading.value = false;
  }
};

const goBackToAuth = () => {
  try {
    sessionStorage.removeItem('audit_token');
  } catch (e) {}
  router.push(`/audit/${electionId}/auth`);
};

onMounted(async () => {
  await loadAuditData();
});
</script>

<template>
  <div class="min-h-screen bg-neutral-100 p-8">
    <div class="max-w-5xl mx-auto">
      <div class="bg-white rounded-lg shadow-lg p-8">
        <div class="mb-8">
          <h1 class="text-3xl font-bold text-blue-600 mb-2">Voting Audit Trail</h1>
          <p v-if="election" class="text-xl text-gray-700">{{ election.title }}</p>
          <p v-if="voter" class="text-sm text-gray-600 mt-1">Voter: {{ voter.name }} ({{ voter.wallet_address }})</p>
        </div>

        <div v-if="loading" class="text-center py-12">
          <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p class="mt-4 text-gray-600">Loading audit data...</p>
        </div>

        <div v-else-if="errorMessage" class="text-center py-12">
          <div class="bg-red-100 border border-red-400 text-red-700 px-6 py-4 rounded-lg inline-block">
            <strong class="font-bold">Error!</strong>
            <p class="mt-2">{{ errorMessage }}</p>
          </div>
          <button
            @click="goBackToAuth"
            class="mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors duration-300"
          >
            Back to Authentication
          </button>
        </div>

        <div v-else-if="votes.length === 0" class="text-center py-12">
          <p class="text-xl text-gray-600">No votes found for this voter in this election.</p>
          <p class="text-sm text-gray-500 mt-2">You may not have voted yet, or your votes are being processed.</p>
          <button
            @click="goBackToAuth"
            class="mt-6 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors duration-300"
          >
            Back to Authentication
          </button>
        </div>

        <div v-else>
          <div class="mb-6">
            <h2 class="text-2xl font-semibold text-gray-800 mb-4">Your Votes</h2>
            <p class="text-sm text-gray-600">Below are the candidates you voted for, along with blockchain verification links.</p>
          </div>

          <div class="space-y-6">
            <div
              v-for="vote in votes"
              :key="vote.id"
              class="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow duration-300"
            >
              <div class="flex items-start gap-6">
                <!-- Candidate Photo -->
                <div class="flex-shrink-0">
                  <img
                    v-if="vote.candidate?.image_url"
                    :src="vote.candidate.image_url"
                    :alt="vote.candidate.name"
                    class="h-24 w-24 rounded-full object-cover border-2 border-blue-200"
                  />
                  <SolarUserBold v-else class="h-24 w-24 text-gray-400" />
                </div>

                <!-- Candidate Details -->
                <div class="flex-1">
                  <div class="mb-3">
                    <h3 class="text-xl font-semibold text-gray-800">{{ vote.candidate?.name || 'Unknown Candidate' }}</h3>
                    <p class="text-sm text-gray-600">Position: {{ vote.position?.title || 'Unknown Position' }}</p>
                  </div>

                  <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div>
                      <span class="font-medium text-gray-700">Status:</span>
                      <span
                        :class="[
                          'ml-2 px-2 py-1 rounded text-xs font-semibold',
                          vote.status === 'confirmed' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'
                        ]"
                      >
                        {{ vote.status || 'pending' }}
                      </span>
                    </div>
                    <div v-if="vote.block_number">
                      <span class="font-medium text-gray-700">Block:</span>
                      <span class="ml-2 text-gray-600">{{ vote.block_number }}</span>
                    </div>
                    <div v-if="vote.created_at">
                      <span class="font-medium text-gray-700">Voted at:</span>
                      <span class="ml-2 text-gray-600">{{ new Date(vote.created_at).toLocaleString() }}</span>
                    </div>
                  </div>

                  <!-- Transaction Hash with Etherscan Link -->
                  <div v-if="vote.tx_hash" class="mt-4 bg-gray-50 p-3 rounded border border-gray-200">
                    <div class="flex items-center justify-between gap-3">
                      <div class="flex-1 min-w-0">
                        <p class="text-xs font-medium text-gray-700 mb-1">Transaction Hash:</p>
                        <p class="text-xs text-gray-600 font-mono break-all">{{ vote.tx_hash }}</p>
                      </div>
                      <a
                        v-if="getEtherscanLink(vote.tx_hash)"
                        :href="getEtherscanLink(vote.tx_hash)"
                        target="_blank"
                        rel="noopener noreferrer"
                        class="flex-shrink-0 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors duration-300 flex items-center gap-2 text-sm font-semibold"
                      >
                        <SolarLinkBold class="w-4 h-4" />
                        View on Etherscan
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="mt-8 flex justify-center gap-4">
            <button
              @click="goBackToAuth"
              class="bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors duration-300"
            >
              Logout
            </button>
            <button
              @click="router.push(`/results/${electionId}`)"
              class="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2 px-6 rounded-lg transition-colors duration-300"
            >
              View Results
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
