<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const form = reactive({
  title: "",
  scheduled_for: "",
  start_time: "",
  end_time: ""
})

const submitCreateElectionForm = () => {
  // Handle form submission logic here
  console.log(form)
  router.push('/dashboard')
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
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:shadow-outline cursor-pointer transition-colors duration-300">
            Create Election
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
