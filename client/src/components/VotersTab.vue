<script setup>
import { ref, reactive } from 'vue';

const totalVotingPool = ref(1000);
const registeredVoters = ref(750);
const castVotes = ref(500);

const voterForm = reactive({
  name: '',
  email: '',
  matricNumber: '',
  image: null, // To store the captured image data
});

const registerVoter = () => {
  console.log('Registering voter:', voterForm);
  // Add logic to handle voter registration (e.g., API call)
  // Reset form
  voterForm.name = '';
  voterForm.email = '';
  voterForm.matricNumber = '';
  voterForm.image = null;
};

const captureImage = () => {
  // Placeholder for camera access and image capture logic
  alert('Camera access not implemented yet. This would open the camera to capture an image.');
  // In a real application, you would use navigator.mediaDevices.getUserMedia
  // to access the camera and then draw the video frame to a canvas to get the image data.
  // voterForm.image = capturedImageData;
};
</script>

<template>
  <div>
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
      <div class="bg-white rounded-lg shadow-inner p-6 text-center">
        <h3 class="text-lg font-semibold text-gray-800 mb-2">Total Voting Pool</h3>
        <p class="text-4xl font-bold text-blue-600">{{ totalVotingPool }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-inner p-6 text-center">
        <h3 class="text-lg font-semibold text-gray-800 mb-2">Registered Voters</h3>
        <p class="text-4xl font-bold text-blue-600">{{ registeredVoters }}</p>
      </div>
      <div class="bg-white rounded-lg shadow-inner p-6 text-center">
        <h3 class="text-lg font-semibold text-gray-800 mb-2">Cast Votes</h3>
        <p class="text-4xl font-bold text-blue-600">{{ castVotes }}</p>
      </div>
    </div>

    <div class="bg-white rounded-lg shadow-inner p-6">
      <h3 class="text-2xl font-bold mb-6">Register Voter</h3>
      <form @submit.prevent="registerVoter">
        <div class="mb-4">
          <label for="voterName" class="block text-gray-700 text-sm font-bold mb-2">Name</label>
          <input v-model="voterForm.name" type="text" id="voterName" class="w-full px-4 py-3 bg-gray-200 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600" placeholder="Enter voter's name">
        </div>
        <div class="mb-4">
          <label for="voterEmail" class="block text-gray-700 text-sm font-bold mb-2">Email</label>
          <input v-model="voterForm.email" type="email" id="voterEmail" class="w-full px-4 py-3 bg-gray-200 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600" placeholder="Enter voter's email">
        </div>
        <div class="mb-4">
          <label for="matricNumber" class="block text-gray-700 text-sm font-bold mb-2">Matric Number</label>
          <input v-model="voterForm.matricNumber" type="text" id="matricNumber" class="w-full px-4 py-3 bg-gray-200 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600" placeholder="Enter matric number">
        </div>
        <div class="mb-6">
          <label class="block text-gray-700 text-sm font-bold mb-2">Voter Image</label>
          <button type="button" @click="captureImage" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg cursor-pointer transition-colors duration-300">Capture Image</button>
          <div v-if="voterForm.image" class="mt-2">
            <img :src="voterForm.image" alt="Voter Image" class="w-32 h-32 object-cover rounded-lg">
          </div>
        </div>
        <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg cursor-pointer transition-colors duration-300">Register Voter</button>
      </form>
    </div>
  </div>
</template>
