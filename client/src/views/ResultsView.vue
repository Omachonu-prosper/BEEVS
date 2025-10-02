<script setup>
import { ref, computed } from 'vue';
import { useRoute } from 'vue-router';

const route = useRoute();
const electionId = route.params.electionId;

const electionResults = ref([
  {
    id: 1,
    title: 'President',
    candidates: [
      { id: 101, name: 'Alice Smith', votes: 120 },
      { id: 102, name: 'Bob Johnson', votes: 150 },
      { id: 103, name: 'Charlie Brown', votes: 80 },
    ],
  },
  {
    id: 2,
    title: 'Vice President',
    candidates: [
      { id: 201, name: 'David Lee', votes: 90 },
      { id: 202, name: 'Eve Davis', votes: 110 },
      { id: 203, name: 'Frank White', votes: 70 },
    ],
  },
  {
    id: 3,
    title: 'Secretary',
    candidates: [
      { id: 301, name: 'Grace Hall', votes: 60 },
      { id: 302, name: 'Henry Green', votes: 130 },
      { id: 303, name: 'Ivy King', votes: 100 },
    ],
  },
]);

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
</script>

<template>
  <div class="min-h-screen bg-neutral-100 p-8">
    <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
      <h1 class="text-3xl font-bold text-blue-600 mb-8 text-center">Election Results for {{ electionId }}</h1>

      <div v-for="position in electionResults" :key="position.id" class="mb-10">
        <h2 class="text-2xl font-semibold text-gray-800 mb-6 border-b-2 border-blue-200 pb-2">{{ position.title }}</h2>
        <div class="space-y-4">
          <div v-for="candidate in position.candidates" :key="candidate.id" class="flex items-center">
            <p class="w-1/4 text-lg font-medium text-gray-700">{{ candidate.name }}</p>
            <div class="w-3/4 bg-gray-200 rounded-full h-6 relative">
              <div 
                :style="{ width: getBarWidth(candidate.votes, getMaxVotes(position.candidates)) }"
                class="bg-blue-500 h-full rounded-full flex items-center justify-end pr-2 text-white text-sm font-bold"
              >
                {{ candidate.votes }}
              </div>
            </div>
          </div>
        </div>
        <p class="text-xl font-bold text-green-600 mt-6 text-center">Winner: {{ getWinner(position.candidates) }}</p>
      </div>
    </div>
  </div>
</template>
