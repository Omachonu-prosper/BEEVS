<script setup>
import { ref, reactive, onMounted, onBeforeUnmount, nextTick } from 'vue';
import { authFetch } from '@/utils/auth';

const props = defineProps({ electionId: [String, Number] });

const totalVotingPool = ref(0);
const registeredVoters = ref(0);
const castVotes = ref(0);

const voterForm = reactive({
  name: '',
  student_record_id: '',
  imageFile: null,
  imagePreview: null,
});

const voters = ref([]);
const loading = ref(false);
const errors = ref([]);
const institutionalRecords = ref([]);
const success = ref('');
const successTimer = ref(null);
const fileInput = ref(null);
const videoRef = ref(null);
const streamRef = ref(null);
const cameraVisible = ref(false);
const activeTab = ref('register'); // 'register' or 'list'

const loadVoters = async () => {
  if (!props.electionId) return;
  loading.value = true;
  try {
    const resp = await authFetch(`/api/v1/elections/${props.electionId}/voters`);
    const json = await resp.json().catch(() => ({}));
  if (!resp.ok) {
      console.error('Failed to load voters', json);
      voters.value = [];
      return;
    }
    voters.value = json?.data?.voters || [];
    registeredVoters.value = voters.value.length;
  } catch (err) {
    console.error(err);
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  loadVoters();
  loadInstitutionalRecords();
});

const loadInstitutionalRecords = async () => {
  if (!props.electionId) return;
  try {
    const resp = await authFetch(`/api/v1/elections/${props.electionId}/institutional-records`);
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      console.error('Failed to load institutional records', json);
      totalVotingPool.value = 0;
      return;
    }
    const recs = json?.data?.records || [];
    institutionalRecords.value = recs;
    totalVotingPool.value = recs.length;
  } catch (err) {
    console.error(err);
    totalVotingPool.value = 0;
  }
};

const onFileChange = (e) => {
  // keep for fallback but not used in UI
  const f = e.target.files && e.target.files[0];
  if (!f) return;
  voterForm.imageFile = f;
  voterForm.imagePreview = URL.createObjectURL(f);
};

const startCamera = async () => {
  // stop any existing stream before starting a new one
  try { stopCamera(); } catch (e) { /* ignore */ }

  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    errors.value.push('Camera not supported in this browser');
    return;
  }
  try {
    // prefer higher resolution and allow environment camera where available
    const constraints = { video: { facingMode: 'environment', width: { ideal: 1280 }, height: { ideal: 720 } }, audio: false };
    let stream = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia(constraints);
    } catch (e) {
      // fallback to default video if environment-facing fails
      stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    }
    streamRef.value = stream;
    // Ensure the video element is mounted before assigning srcObject
    cameraVisible.value = true;
    await nextTick();
    if (videoRef.value) {
      videoRef.value.srcObject = stream;
      // wait for metadata so videoWidth/videoHeight are available and frames start
      await new Promise((resolve) => {
        const v = videoRef.value;
        const onLoaded = () => {
          v.removeEventListener('loadedmetadata', onLoaded);
          resolve();
        };
        v.addEventListener('loadedmetadata', onLoaded);
        // safety timeout
        setTimeout(() => resolve(), 1000);
      });
      try { await videoRef.value.play(); } catch (e) { /* ignore play failure */ }
    }
  } catch (err) {
    console.error('Failed to access camera', err);
    errors.value.push('Failed to access camera: ' + (err?.message || err));
  }
};

onBeforeUnmount(() => {
  // ensure camera is stopped when component unmounts
  try { stopCamera(); } catch (e) { /* ignore */ }
  if (successTimer.value) {
    clearTimeout(successTimer.value);
    successTimer.value = null;
  }
});

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
  // if video dimensions are not yet available, wait a little for them to populate
  const ensureDimensions = async () => {
    let attempts = 0;
    while ((video.videoWidth === 0 || video.videoHeight === 0) && attempts < 5) {
      await new Promise((r) => setTimeout(r, 150));
      attempts += 1;
    }
  };
  await ensureDimensions();
  canvas.width = video.videoWidth || 1280;
  canvas.height = video.videoHeight || 720;
  const ctx = canvas.getContext('2d');
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  canvas.toBlob((blob) => {
    if (!blob) {
      errors.value.push('Failed to capture image');
      return;
    }
    const file = new File([blob], `voter_${Date.now()}.jpg`, { type: blob.type });
    // revoke previous preview
    if (voterForm.imagePreview) URL.revokeObjectURL(voterForm.imagePreview);
    voterForm.imageFile = file;
    voterForm.imagePreview = URL.createObjectURL(blob);
    stopCamera();
  }, 'image/jpeg', 0.9);
};

const clearForm = () => {
  voterForm.name = '';
  voterForm.student_record_id = '';
  voterForm.imageFile = null;
  voterForm.imagePreview && URL.revokeObjectURL(voterForm.imagePreview);
  voterForm.imagePreview = null;
};

const registerVoter = async () => {
  errors.value = [];
  if (!voterForm.name || !voterForm.student_record_id || !voterForm.imageFile) {
    errors.value.push('Please provide name, registration number, and capture an image.');
    return;
  }
  if (!props.electionId) {
    errors.value.push('Missing election id');
    return;
  }

  const form = new FormData();
  form.append('name', voterForm.name);
  form.append('student_record_id', voterForm.student_record_id);
  form.append('election_id', props.electionId);
  form.append('image', voterForm.imageFile);

  try {
    const resp = await authFetch('/api/v1/voters', { method: 'POST', body: form });
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      // Normalize API error shape to an array of messages for display
      const msgs = [];
      if (json && typeof json === 'object') {
        if (json.errors && typeof json.errors === 'object' && Object.keys(json.errors).length > 0) {
          for (const k of Object.keys(json.errors)) {
            const val = json.errors[k];
            if (Array.isArray(val)) msgs.push(...val);
            else if (val) msgs.push(val);
          }
        }
        if (msgs.length === 0 && json.message) msgs.push(json.message);
      }
      if (msgs.length === 0) msgs.push('Registration failed');
      errors.value = msgs;
      return;
    }
    // success
    errors.value = [];
    success.value = json?.message || 'Voter registered successfully';
    // clear any previous timer
    if (successTimer.value) {
      clearTimeout(successTimer.value);
      successTimer.value = null;
    }
    successTimer.value = setTimeout(() => { success.value = ''; successTimer.value = null; }, 4000);
    clearForm();
    await loadVoters();
    await loadInstitutionalRecords();
  } catch (err) {
    console.error(err);
    errors.value = [err?.message || 'Registration failed'];
  }
};

const deleteVoter = async (id) => {
  if (!confirm('Delete this voter?')) return;
  try {
    const resp = await authFetch(`/api/v1/voters/${id}`, { method: 'DELETE' });
    if (!resp.ok) throw new Error('Failed to delete voter');
    await loadVoters();
    await loadInstitutionalRecords();
  } catch (err) {
    console.error(err);
    errors.value.push(err?.message || 'Delete failed');
  }
};

const getRegistrationNumber = (recordId) => {
  if (!recordId) return '';
  const r = institutionalRecords.value.find((x) => String(x.id) === String(recordId));
  return r ? r.registration_number : String(recordId);
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

    <!-- subtabs -->
    <div class="mb-6">
      <div class="flex gap-3">
        <button :class="['px-4 py-2 rounded', activeTab === 'register' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border']" @click="activeTab = 'register'">Register Voter</button>
        <button :class="['px-4 py-2 rounded', activeTab === 'list' ? 'bg-blue-600 text-white' : 'bg-white text-gray-700 border']" @click="activeTab = 'list'">Registered Voters</button>
      </div>
    </div>

    <div v-if="activeTab === 'register'" class="bg-white rounded-lg shadow-inner p-6 mb-6">
      <h3 class="text-2xl font-bold mb-6">Register Voter</h3>
      <form @submit.prevent="registerVoter">
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">Name</label>
          <input v-model="voterForm.name" type="text" class="w-full px-4 py-3 bg-gray-200 border border-gray-300 rounded-lg" placeholder="Enter voter's name" />
        </div>
        <!-- email removed: not required -->
        <div class="mb-4">
          <label class="block text-gray-700 text-sm font-bold mb-2">Registration Number</label>
          <input v-model="voterForm.student_record_id" type="text" class="w-full px-4 py-3 bg-gray-200 border border-gray-300 rounded-lg" placeholder="Enter registration number (e.g. REG12345)" />
          <div v-if="institutionalRecords.length === 0" class="text-sm text-neutral-500 mt-2">No institutional records found for this election.</div>
        </div>
        <div class="mb-6">
          <label class="block text-gray-700 text-sm font-bold mb-2">Voter Image (capture only)</label>
          <div class="flex flex-col gap-3">
            <div>
              <button type="button" @click="startCamera" class="bg-white border border-gray-300 px-3 py-2 rounded-lg">Open Camera</button>
            </div>
            <div v-if="cameraVisible" class="flex flex-col items-center gap-2">
              <video ref="videoRef" class="w-96 h-72 md:w-[640px] md:h-[480px] bg-black rounded object-cover" autoplay playsinline muted></video>
              <div class="flex gap-2">
                <button type="button" @click="capturePhoto" class="bg-blue-600 text-white px-3 py-2 rounded">Capture</button>
                <button type="button" @click="stopCamera" class="bg-gray-200 px-3 py-2 rounded">Close</button>
              </div>
            </div>
            <div v-else class="flex items-center gap-3">
              <div v-if="voterForm.imagePreview">
                <img :src="voterForm.imagePreview" class="w-24 h-24 object-cover rounded" />
              </div>
              <div v-else class="text-sm text-neutral-500">No photo captured</div>
            </div>
          </div>
        </div>
        <div v-if="success" class="mb-4 text-green-600">
          {{ success }}
        </div>
        <div v-if="errors.length" class="mb-4 text-red-600">
          <ul>
            <li v-for="(e,i) in errors" :key="i">{{ e }}</li>
          </ul>
        </div>
        <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg">Register Voter</button>
      </form>
    </div>

    <div v-if="activeTab === 'list'" class="bg-white rounded-lg shadow-inner p-6">
      <h3 class="text-2xl font-bold mb-4">Registered Voters</h3>
      <div v-if="loading">Loading...</div>
      <div v-else>
        <div v-if="voters.length === 0" class="text-neutral-600">No registered voters yet.</div>
        <table v-else class="min-w-full text-sm">
          <thead>
            <tr class="text-left">
              <th class="px-4 py-2">Name</th>
              <th class="px-4 py-2">Reg. No</th>
              <th class="px-4 py-2">Wallet</th>
              <th class="px-4 py-2">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="v in voters" :key="v.id" class="border-t">
              <td class="px-4 py-2">{{ v.name }}</td>
              <td class="px-4 py-2">{{ getRegistrationNumber(v.student_record_id) }}</td>
              <td class="px-4 py-2">{{ v.wallet_address }}</td>
              <td class="px-4 py-2"><button @click="deleteVoter(v.id)" class="text-red-600">Delete</button></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
