<script setup>
import { ref, onMounted } from 'vue';
import { authFetch } from '@/utils/auth';

const props = defineProps({
  electionId: [String, Number]
});

const hasRecords = ref(false);
const selectedFile = ref(null);
const uploading = ref(false);
const uploadResult = ref(null);
const uploadErrors = ref([]);
const fileInput = ref(null);
const records = ref([]);

const onFileChange = (e) => {
  const f = e.target.files && e.target.files[0];
  selectedFile.value = f || null;
  uploadResult.value = null;
  uploadErrors.value = [];
};

const triggerFileSelect = () => {
  if (fileInput.value) fileInput.value.click();
};

const loadRecords = async () => {
  if (!props.electionId) return;
  try {
    const resp = await authFetch(`/api/v1/elections/${props.electionId}/institutional-records`);
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      console.error('Failed to load records', json);
      records.value = [];
      hasRecords.value = false;
      return;
    }
    records.value = json?.data?.records || [];
    hasRecords.value = records.value.length > 0;
  } catch (err) {
    console.error(err);
    records.value = [];
    hasRecords.value = false;
  }
};

onMounted(() => {
  loadRecords();
});

const clearSelection = () => {
  selectedFile.value = null;
  uploadResult.value = null;
  uploadErrors.value = [];
  if (fileInput.value) fileInput.value.value = null;
};

const uploadFile = async () => {
  uploadErrors.value = [];
  uploadResult.value = null;
  if (!selectedFile.value) {
    uploadErrors.value.push('Please choose a CSV file to upload.');
    return;
  }
  if (!props.electionId) {
    uploadErrors.value.push('Missing election id.');
    return;
  }

  uploading.value = true;
  try {
    const form = new FormData();
    form.append('file', selectedFile.value);
    // include election id in the URL (same pattern as other components)
    const resp = await authFetch(`/api/v1/elections/${props.electionId}/institutional-records/upload`, { method: 'POST', body: form });
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      // Show validation errors from server if present
      if (json?.errors) {
        // errors may be array of row errors or dict
        uploadErrors.value = Array.isArray(json.errors) ? json.errors : [json.errors];
      } else if (json?.message) {
        uploadErrors.value = [json.message];
      } else {
        uploadErrors.value = ['Upload failed'];
      }
      return;
    }

    uploadResult.value = json?.data || null;
    if (uploadResult.value && uploadResult.value.saved_count > 0) {
      await loadRecords();
    }
    // clear selection after successful upload
    selectedFile.value = null;
    if (fileInput.value) fileInput.value.value = null;
  } catch (err) {
    console.error(err);
    uploadErrors.value.push(err?.message || 'Upload failed');
  } finally {
    uploading.value = false;
  }
};

const deleteRecord = async (recordId) => {
  if (!confirm('Delete this record?')) return;
  try {
    const resp = await authFetch(`/api/v1/institutional-records/${recordId}`, { method: 'DELETE' });
    if (!resp.ok) throw new Error('Failed to delete');
    await loadRecords();
  } catch (err) {
    console.error(err);
    uploadErrors.value.push(err?.message || 'Failed to delete record');
  }
};

const deleteAllRecords = async () => {
  if (!confirm('Delete ALL institutional records for this election? This cannot be undone.')) return;
  try {
    const resp = await authFetch(`/api/v1/elections/${props.electionId}/institutional-records`, { method: 'DELETE' });
    if (!resp.ok) throw new Error('Failed to delete all records');
    await loadRecords();
  } catch (err) {
    console.error(err);
    uploadErrors.value.push(err?.message || 'Failed to delete records');
  }
};

const downloadRecords = () => {
  // No GET endpoint implemented yet; placeholder
  alert('Download not implemented yet.');
};
</script>

<template>
  <div>
    <h2 class="text-2xl font-bold mb-6">Institutional Records</h2>

    <div class="bg-white rounded-lg shadow-inner p-6">
      <!-- Conditional rendering will go here in a later iteration -->
      <div class="text-center">
        <p class="text-lg text-gray-700 mb-4">Upload a CSV file (required columns: name, registration_number, department, faculty, level). You can upload additional files even if records exist.</p>
        <!-- hidden native file input; trigger via Choose File button -->
        <input ref="fileInput" type="file" @change="onFileChange" accept=".csv" class="hidden" />
        <div class="mt-4 flex items-center justify-center gap-3">
          <button @click="triggerFileSelect" type="button" class="bg-white border border-gray-300 px-3 py-2 rounded-lg hover:bg-gray-50">Choose File</button>
          <div class="text-sm text-gray-700">{{ selectedFile ? selectedFile.name : 'No file chosen' }}</div>
          <button @click="clearSelection" type="button" class="bg-gray-200 hover:bg-gray-300 text-gray-800 font-bold py-2 px-4 rounded">Clear</button>
          <button @click="uploadFile" :disabled="uploading" type="button" class="bg-blue-600 disabled:opacity-50 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">{{ uploading ? 'Uploading...' : 'Upload CSV' }}</button>
        </div>
        <div v-if="uploadErrors.length" class="mt-4 text-left max-w-3xl mx-auto">
          <h4 class="font-semibold text-red-600 mb-2">Errors</h4>
          <ul class="list-disc pl-6 text-sm text-red-600">
            <li v-for="(err, i) in uploadErrors" :key="i">{{ typeof err === 'string' ? err : JSON.stringify(err) }}</li>
          </ul>
        </div>
        <div v-if="uploadResult" class="mt-4 text-left max-w-3xl mx-auto">
          <h4 class="font-semibold text-green-600 mb-2">Upload Result</h4>
          <p class="text-sm">Saved: {{ uploadResult.saved_count }}</p>
          <div v-if="uploadResult.errors && uploadResult.errors.length" class="mt-2">
            <h5 class="font-medium">Row errors:</h5>
            <ul class="list-disc pl-6 text-sm text-red-600">
              <li v-for="(e, idx) in uploadResult.errors" :key="idx">Row {{ e.row }}: {{ JSON.stringify(e.errors) }}</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="mt-8">
        <h3 class="text-xl font-semibold mb-4">Institutional Records</h3>
        <div v-if="records.length === 0" class="text-neutral-600">No records for this election yet.</div>
        <div v-else>
          <div class="mb-4 flex justify-end">
            <button @click="deleteAllRecords" class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded">Delete All Records</button>
          </div>
          <div class="overflow-x-auto">
            <table class="min-w-full text-sm">
              <thead>
                <tr class="text-left">
                  <th class="px-4 py-2">Name</th>
                  <th class="px-4 py-2">Reg. No</th>
                  <th class="px-4 py-2">Department</th>
                  <th class="px-4 py-2">Faculty</th>
                  <th class="px-4 py-2">Level</th>
                  <th class="px-4 py-2">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="rec in records" :key="rec.id" class="border-t">
                  <td class="px-4 py-2">{{ rec.name }}</td>
                  <td class="px-4 py-2">{{ rec.registration_number }}</td>
                  <td class="px-4 py-2">{{ rec.department }}</td>
                  <td class="px-4 py-2">{{ rec.faculty }}</td>
                  <td class="px-4 py-2">{{ rec.level }}</td>
                  <td class="px-4 py-2">
                    <button @click="deleteRecord(rec.id)" class="text-red-600 hover:text-red-800">Delete</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
