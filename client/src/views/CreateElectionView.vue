<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { authFetch, getAccessToken } from '@/utils/auth'

const router = useRouter()

const form = reactive({
  title: "",
  scheduled_for: "",
  start_time: "",
  end_time: ""
})

const loading = ref(false)
const error = ref('')

const submitCreateElectionForm = async () => {
  error.value = ''
  loading.value = true
  try {
    if (!form.title || !form.scheduled_for || !form.start_time || !form.end_time) {
      error.value = 'Please fill all fields.'
      return
    }

    // Build ISO datetimes for starts_at and ends_at
    const starts_at = new Date(`${form.scheduled_for}T${form.start_time}:00`).toISOString()
    const ends_at = new Date(`${form.scheduled_for}T${form.end_time}:00`).toISOString()

    const payload = {
      title: form.title,
      scheduled_for: form.scheduled_for,
      starts_at,
      ends_at
    }

    // Ensure we have an access token before attempting the request
    const token = getAccessToken()
    if (!token) {
      error.value = 'Not authenticated. Please login.'
      return
    }

    // Use a relative API path; authFetch will prefix the API base and attach the
    // Authorization header automatically.
    const resp = await authFetch(`/api/v1/elections`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify(payload)
    })

    const json = await resp.json().catch(() => ({}))
    if (!resp.ok) {
      error.value = json?.message || 'Failed to create election'
      return
    }

    // Success. Redirect to dashboard (or election page if desired)
    router.push('/dashboard')
  } catch (err) {
    console.error(err)
    error.value = err?.message || 'An error occurred'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-neutral-100 flex items-center justify-center">
    <div class="max-w-lg w-full bg-white rounded-lg shadow-lg p-8">
      <h2 class="text-3xl font-bold text-center text-primary mb-8">Create New Election</h2>
      <form @submit.prevent="submitCreateElectionForm">
        <div class="mb-6">
          <label for="title" class="block text-neutral-700 text-sm font-bold mb-2">Election Title</label>
          <input 
            v-model="form.title" type="text" id="title" name="title"
            class="w-full px-4 py-3 bg-neutral-200 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Enter election title">
        </div>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <div>
            <label for="scheduled_for" class="block text-neutral-700 text-sm font-bold mb-2">Scheduled Date</label>
            <input 
              v-model="form.scheduled_for" type="date" id="scheduled_for" name="scheduled_for"
              class="w-full px-4 py-3 bg-neutral-200 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary">
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="start_time" class="block text-neutral-700 text-sm font-bold mb-2">Start Time</label>
              <input 
                v-model="form.start_time" type="time" id="start_time" name="start_time"
                class="w-full px-4 py-3 bg-neutral-200 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary">
            </div>
            <div>
              <label for="end_time" class="block text-neutral-700 text-sm font-bold mb-2">End Time</label>
              <input 
                v-model="form.end_time" type="time" id="end_time" name="end_time"
                class="w-full px-4 py-3 bg-neutral-200 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary">
            </div>
          </div>
        </div>
        <div class="flex items-center justify-center">
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:shadow-outline cursor-pointer transition-colors duration-300 disabled:opacity-60 disabled:cursor-not-allowed flex items-center justify-center">
            <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
            </svg>
            <span v-if="!loading">Create Election</span>
            <span v-else>Creating...</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
