<script setup>
import { ref, onMounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import SolarCameraBold from '~icons/solar/camera-bold';
import { authFetch } from '@/utils/auth';

const route = useRoute();
const router = useRouter();
const electionId = route.params.electionId;

const registrationNumber = ref('');
const cameraOpen = ref(false);
const videoElement = ref(null);
const canvasElement = ref(null);
const capturedImage = ref(null);
const stream = ref(null);
const loading = ref(false);
const errorMessage = ref('');
const electionTitle = ref('');

const loadElectionTitle = async () => {
    if (!electionId) return;
    try {
        const resp = await authFetch(`/api/v1/elections`);
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

onMounted(() => {
  loadElectionTitle();
});

const openCamera = async () => {
  try {
    // Close any existing stream first
    if (stream.value) {
      stream.value.getTracks().forEach(track => track.stop());
      stream.value = null;
    }

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      errorMessage.value = 'Camera not supported in this browser';
      return;
    }

    const constraints = { video: { facingMode: 'user', width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false };
    let mediaStream = null;
    try {
      mediaStream = await navigator.mediaDevices.getUserMedia(constraints);
    } catch (e) {
      // Fallback to basic video constraints
      mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    }

    stream.value = mediaStream;
    cameraOpen.value = true;
    errorMessage.value = '';

    // Wait for DOM to update
    await nextTick();

    if (videoElement.value) {
      videoElement.value.srcObject = mediaStream;
      
      // Wait for video metadata to load
      await new Promise((resolve) => {
        const video = videoElement.value;
        const onLoaded = () => {
          video.removeEventListener('loadedmetadata', onLoaded);
          resolve();
        };
        video.addEventListener('loadedmetadata', onLoaded);
        // Timeout as fallback
        setTimeout(() => resolve(), 1000);
      });

      // Start playing the video
      try {
        await videoElement.value.play();
      } catch (e) {
        console.error('Failed to play video', e);
      }
    }
  } catch (err) {
    console.error('Error accessing camera', err);
    errorMessage.value = 'Failed to access camera. Please check permissions.';
  }
};

const closeCamera = () => {
  if (stream.value) {
    stream.value.getTracks().forEach(track => track.stop());
    stream.value = null;
  }
  if (videoElement.value) {
    try {
      videoElement.value.pause();
    } catch (e) {}
    videoElement.value.srcObject = null;
  }
  cameraOpen.value = false;
};

const captureImage = async () => {
  if (canvasElement.value && videoElement.value) {
    const canvas = canvasElement.value;
    const video = videoElement.value;

    // Ensure video dimensions are available
    let attempts = 0;
    while ((video.videoWidth === 0 || video.videoHeight === 0) && attempts < 5) {
      await new Promise((r) => setTimeout(r, 150));
      attempts += 1;
    }

    // Center-crop to square
    const vw = video.videoWidth || 1280;
    const vh = video.videoHeight || 720;
    const size = Math.min(vw, vh);
    const sx = Math.max(0, Math.floor((vw - size) / 2));
    const sy = Math.max(0, Math.floor((vh - size) / 2));

    // Set square canvas
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');
    
    // Draw the centered square region from video onto the square canvas
    ctx.drawImage(video, sx, sy, size, size, 0, 0, size, size);
    
    capturedImage.value = canvas.toDataURL('image/jpeg', 0.9);
    closeCamera();
  }
};

const retakeImage = () => {
  capturedImage.value = null;
  openCamera();
};

const authenticate = async () => {
    if (!registrationNumber.value.trim()) {
        errorMessage.value = 'Please enter your registration number';
        return;
    }

    if (!capturedImage.value) {
        errorMessage.value = 'Please capture your image';
        return;
    }

    loading.value = true;
    errorMessage.value = '';

    try {
        const formData = new FormData();
        formData.append('registration_number', registrationNumber.value.trim());

        // Convert base64 to blob
        const blob = await fetch(capturedImage.value).then(r => r.blob());
        formData.append('image', blob, 'capture.jpg');

        const resp = await authFetch(`/api/v1/elections/${electionId}/audit-auth`, {
            method: 'POST',
            body: formData,
        });

        const json = await resp.json().catch(() => ({}));

        if (!resp.ok) {
            errorMessage.value = json?.message || 'Authentication failed';
            loading.value = false;
            return;
        }

        const token = json?.data?.token;
        if (token) {
            try {
                sessionStorage.setItem('audit_token', token);
            } catch (e) {
                console.error('Failed to save audit token to sessionStorage', e);
            }
            router.push(`/audit/${electionId}`);
        } else {
            errorMessage.value = 'No token received from server';
        }
    } catch (err) {
        console.error('Error during authentication', err);
        errorMessage.value = err?.message || 'An error occurred during authentication';
    } finally {
        loading.value = false;
    }
};
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 to-blue-100 flex items-center justify-center p-4">
    <div class="bg-white rounded-2xl shadow-2xl w-full max-w-lg p-8">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-blue-600 mb-2">Audit Authentication</h1>
        <p class="text-gray-600">{{ electionTitle || `Election ${electionId}` }}</p>
        <p class="text-sm text-gray-500 mt-2">Authenticate to view your voting audit trail</p>
      </div>

      <div v-if="errorMessage" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
        {{ errorMessage }}
      </div>

      <div class="space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Registration Number</label>
          <input
            v-model="registrationNumber"
            type="text"
            placeholder="e.g., CS/2020/001"
            class="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            :disabled="loading"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">Face Verification</label>
          
          <div v-if="!cameraOpen && !capturedImage" class="text-center">
            <button
              @click="openCamera"
              class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-300 flex items-center justify-center gap-2"
              :disabled="loading"
            >
              <SolarCameraBold class="w-5 h-5" />
              Open Camera
            </button>
          </div>

          <div v-if="cameraOpen" class="space-y-4">
            <div class="relative bg-black rounded-lg overflow-hidden">
              <video ref="videoElement" autoplay playsinline class="w-full"></video>
            </div>
            <div class="flex gap-3">
              <button
                @click="captureImage"
                class="flex-1 bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-300"
              >
                Capture
              </button>
              <button
                @click="closeCamera"
                class="flex-1 bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-300"
              >
                Cancel
              </button>
            </div>
          </div>

          <div v-if="capturedImage && !cameraOpen" class="space-y-4">
            <div class="relative bg-black rounded-lg overflow-hidden">
              <img :src="capturedImage" alt="Captured" class="w-full" />
            </div>
            <button
              @click="retakeImage"
              class="w-full bg-gray-600 hover:bg-gray-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors duration-300"
            >
              Retake Image
            </button>
          </div>
        </div>

        <button
          @click="authenticate"
          :disabled="loading || !registrationNumber.trim() || !capturedImage"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-colors duration-300 disabled:bg-gray-400 disabled:cursor-not-allowed flex items-center justify-center"
        >
          <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
          </svg>
          <span v-if="!loading">Authenticate</span>
          <span v-else>Authenticating...</span>
        </button>
      </div>

      <canvas ref="canvasElement" style="display: none;"></canvas>
    </div>
  </div>
</template>
