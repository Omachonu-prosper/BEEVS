<script setup>
import { ref, reactive } from 'vue';
import { useRoute } from 'vue-router';
import SolarUserBold from '~icons/solar/user-bold';

const route = useRoute();
const electionId = route.params.electionId;

const positions = reactive([
  {
    id: 1,
    title: 'President',
    candidates: [
      { id: 101, name: 'Alice Smith', selected: false },
      { id: 102, name: 'Bob Johnson', selected: false },
      { id: 103, name: 'Charlie Brown', selected: false },
    ],
  },
  {
    id: 2,
    title: 'Vice President',
    candidates: [
      { id: 201, name: 'David Lee', selected: false },
      { id: 202, name: 'Eve Davis', selected: false },
      { id: 203, name: 'Frank White', selected: false },
    ],
  },
  {
    id: 3,
    title: 'Secretary',
    candidates: [
      { id: 301, name: 'Grace Hall', selected: false },
      { id: 302, name: 'Henry Green', selected: false },
      { id: 303, name: 'Ivy King', selected: false },
    ],
  },
]);

const selectCandidate = (positionId, candidateId) => {
  const position = positions.find(p => p.id === positionId);
  if (position) {
    position.candidates.forEach(c => (c.selected = false)); // Deselect all in this position
    const candidate = position.candidates.find(c => c.id === candidateId);
    if (candidate) {
      candidate.selected = true; // Select the chosen candidate
    }
  }
};

const submitVotes = () => {
  const selectedVotes = positions.map(position => ({
    positionId: position.id,
    positionTitle: position.title,
    selectedCandidate: position.candidates.find(c => c.selected),
  }));
  console.log('Submitted Votes:', selectedVotes);
  alert('Votes submitted successfully!');
  // Here you would typically send this data to your backend
};
</script>

<template>
  <div class="min-h-screen bg-neutral-100 p-8">
    <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-8">
      <h1 class="text-3xl font-bold text-blue-600 mb-8 text-center">Cast Your Vote for {{ electionId }}</h1>

      <div v-for="position in positions" :key="position.id" class="mb-10">
        <h2 class="text-2xl font-semibold text-gray-800 mb-6 border-b-2 border-blue-200 pb-2">{{ position.title }}</h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          <div
            v-for="candidate in position.candidates" :key="candidate.id"
            @click="selectCandidate(position.id, candidate.id)"
            :class="[
              'bg-gray-100 p-6 rounded-lg shadow-md cursor-pointer transition-all duration-200',
              candidate.selected ? 'border-2 border-blue-600 ring-2 ring-blue-300' : 'hover:shadow-lg hover:border-blue-300 border-2 border-transparent'
            ]"
          >
            <div class="flex flex-col items-center">
              <SolarUserBold class="h-16 w-16 text-gray-500 mb-4" />
              <p class="text-lg font-medium text-gray-700 text-center">{{ candidate.name }}</p>
            </div>
          </div>
        </div>
        <p v-if="position.candidates.some(c => c.selected)" class="mt-4 text-lg text-blue-600 font-semibold text-center">
          Selected: {{ position.candidates.find(c => c.selected).name }}
        </p>
      </div>

      <div class="mt-10 text-center">
        <button
          @click="submitVotes"
          class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg cursor-pointer transition-colors duration-300 text-xl"
        >
          Submit Votes
        </button>
      </div>
    </div>
  </div>
</template>
