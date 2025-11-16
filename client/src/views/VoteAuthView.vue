<script setup>
import { ref, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';

const route = useRoute();
const router = useRouter();
const electionId = route.params.electionId;

const videoRef = ref(null);
const streamRef = ref(null);
const cameraVisible = ref(false);
const registrationNumber = ref('');
const imageFile = ref(null);
const imagePreview = ref(null);
const errors = ref([]);
const loading = ref(false);

const startCamera = async () => {
  try { stopCamera(); } catch (e) { }
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    errors.value.push('Camera not supported in this browser');
    return;
  }
  try {
    const constraints = { video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false };
    let stream = null;
    try { stream = await navigator.mediaDevices.getUserMedia(constraints); } catch (e) { stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false }); }
    streamRef.value = stream;
    cameraVisible.value = true;
    await nextTick();
    if (videoRef.value) {
      videoRef.value.srcObject = stream;
      await new Promise((resolve) => {
        const v = videoRef.value;
        const onLoaded = () => { v.removeEventListener('loadedmetadata', onLoaded); resolve(); };
        v.addEventListener('loadedmetadata', onLoaded);
        setTimeout(() => resolve(), 1000);
      });
      try { await videoRef.value.play(); } catch (e) { }
    }
  } catch (err) {
    console.error('Failed to access camera', err);
    errors.value.push('Failed to access camera: ' + (err?.message || err));
  }
};

const stopCamera = () => {
  if (streamRef.value) {
    streamRef.value.getTracks().forEach((t) => t.stop());
    streamRef.value = null;
  }
  if (videoRef.value) {
    try { videoRef.value.pause(); } catch (e) {}
    videoRef.value.srcObject = null;
  }
  cameraVisible.value = false;
};

const capturePhoto = async () => {
  if (!videoRef.value) return;
  const video = videoRef.value;
    const canvas = document.createElement('canvas');
    const ensureDimensions = async () => {
      let attempts = 0;
      while ((video.videoWidth === 0 || video.videoHeight === 0) && attempts < 5) {
        await new Promise((r) => setTimeout(r, 150));
        attempts += 1;
      }
    };
    await ensureDimensions();

    // center-crop to square
    const vw = video.videoWidth || 1280;
    const vh = video.videoHeight || 720;
    const size = Math.min(vw, vh);
    const sx = Math.max(0, Math.floor((vw - size) / 2));
    const sy = Math.max(0, Math.floor((vh - size) / 2));

    // set square canvas
    canvas.width = size;
    canvas.height = size;
    const ctx = canvas.getContext('2d');
    // draw the centered square region from video onto the square canvas
    ctx.drawImage(video, sx, sy, size, size, 0, 0, size, size);

    canvas.toBlob((blob) => {
      if (!blob) { errors.value.push('Failed to capture image'); return; }
      const file = new File([blob], `live_${Date.now()}.jpg`, { type: blob.type });
      imageFile.value = file;
      // revoke previous preview URL if any
      if (imagePreview.value) try { URL.revokeObjectURL(imagePreview.value); } catch (e) {}
      imagePreview.value = URL.createObjectURL(blob);
      stopCamera();
    }, 'image/jpeg', 0.9);
};

onBeforeUnmount(() => { try { stopCamera(); } catch (e) {} });

const submitAuth = async () => {
  errors.value = [];
  if (!registrationNumber.value) { errors.value.push('Please enter registration number'); return; }
  if (!imageFile.value) { errors.value.push('Please capture a live photo'); return; }
  loading.value = true;
  try {
    const form = new FormData();
    form.append('registration_number', registrationNumber.value.trim());
    form.append('image', imageFile.value);

    const resp = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000'}/api/v1/elections/${electionId}/vote-auth`, {
      method: 'POST',
      body: form,
      mode: 'cors'
    });
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      const msgs = [];
      if (json && typeof json === 'object') {
        if (json.errors && typeof json.errors === 'object' && Object.keys(json.errors).length > 0) {
          for (const k of Object.keys(json.errors)) {
            const val = json.errors[k];
            if (Array.isArray(val)) msgs.push(...val); else if (val) msgs.push(val);
          }
        }
        if (msgs.length === 0 && json.message) msgs.push(json.message);
      }
      if (msgs.length === 0) msgs.push('Authentication failed');
      errors.value = msgs;
      return;
    }

    const token = json?.data?.token;
    if (!token) { errors.value.push('No token returned from server'); return; }

    // store vote auth token in session storage (short lived)
    try { sessionStorage.setItem('vote_token', token); } catch (e) { console.warn('Failed to set session storage', e); }

    // redirect to voting page
    router.push(`/vote/${electionId}`);
  } catch (err) {
    console.error(err);
    errors.value = [err?.message || 'Authentication failed'];
  } finally { loading.value = false; }
};

onMounted(() => { /* nothing for now */ });
</script>

<template>
  <div class="min-h-screen bg-neutral-100 p-8">
    <div class="max-w-3xl mx-auto bg-white rounded-lg shadow-lg p-8">
      <h1 class="text-2xl font-bold text-center mb-4">Voter Authentication</h1>
      <p class="text-sm text-neutral-600 mb-4">Enter your registration number and capture a live photo to verify your identity before voting.</p>

      <div class="mb-4">
        <label class="block text-sm font-medium mb-2">Registration Number</label>
        <input v-model="registrationNumber" type="text" class="w-full px-4 py-3 bg-gray-100 border rounded" placeholder="e.g. REG12345" />
      </div>

      <div class="mb-4">
        <label class="block text-sm font-medium mb-2">Live Photo</label>
        <div>
          <div class="flex gap-2 mb-2">
            <button @click="startCamera" type="button" class="px-3 py-2 bg-white border rounded">Open Camera</button>
            <button @click="capturePhoto" type="button" class="px-3 py-2 bg-blue-600 text-white rounded">Capture</button>
            <button @click="stopCamera" type="button" class="px-3 py-2 bg-gray-200 rounded">Close</button>
          </div>
          <div v-if="cameraVisible" class="flex justify-center mb-2">
            <video ref="videoRef" class="w-full h-64 bg-black rounded object-cover" autoplay playsinline muted></video>
          </div>
          <div v-else class="flex items-center gap-3">
            <div v-if="imagePreview"><img :src="imagePreview" class="w-40 h-40 object-cover rounded" /></div>
            <div v-else class="text-sm text-neutral-500">No photo captured</div>
          </div>
        </div>
      </div>

      <div v-if="errors.length" class="mb-4 text-red-600">
        <ul>
          <li v-for="(e,i) in errors" :key="i">{{ e }}</li>
        </ul>
      </div>

      <div class="flex justify-end">
        <button @click="submitAuth" class="px-6 py-3 bg-blue-600 text-white rounded" :disabled="loading">{{ loading ? 'Verifying...' : 'Verify & Continue' }}</button>
      </div>
    </div>
  </div>
</template>
