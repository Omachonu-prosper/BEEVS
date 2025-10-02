<script setup>
import { ref } from 'vue';

const hasRecords = ref(false); // Placeholder for whether records exist
const selectedFile = ref(null);

const handleFileUpload = (event) => {
  selectedFile.value = event.target.files[0];
  if (selectedFile.value) {
    console.log('Selected file:', selectedFile.value.name);
    // In a real application, you would upload this file to a server
    alert(`File ${selectedFile.value.name} selected for upload.`);
    // For demonstration, let's assume a successful upload sets hasRecords to true
    hasRecords.value = true;
  }
};

const downloadRecords = () => {
  alert('Downloading institutional records...');
  // In a real application, this would trigger a file download
};
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Institutional Records</h2>

    <div class="bg-white rounded-lg shadow-inner p-6">
      <!-- Conditional rendering will go here in a later iteration -->
      <div v-if="hasRecords" class="text-center">
        <p class="text-lg text-gray-700 mb-4">Records are available for download.</p>
        <button @click="downloadRecords" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg cursor-pointer transition-colors duration-300">Download Records</button>
      </div>
      <div v-else class="text-center">
        <p class="text-lg text-gray-700 mb-4">No records uploaded yet. Upload a CSV or Excel file.</p>
        <input type="file" @change="handleFileUpload" accept=".csv, .xlsx" class="block w-full text-sm text-gray-500
            file:mr-4 file:py-2 file:px-4
            file:rounded-full file:border-0
            file:text-sm file:font-semibold
            file:bg-blue-50 file:text-blue-700
            hover:file:bg-blue-100 cursor-pointer
          "/>
      </div>
    </div>
  </div>
</template>
