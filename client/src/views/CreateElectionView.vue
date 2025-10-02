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
  <div class="min-h-screen bg-gray-100 flex items-center justify-center">
    <div class="max-w-md w-full bg-white rounded-lg shadow-md p-8">
      <h2 class="text-2xl font-bold text-center text-gray-800 mb-8">Create New Election</h2>
      <form>
        <div class="mb-4">
          <label for="title" class="block text-gray-700 text-sm font-bold mb-2">Election Title</label>
          <input 
            v-model="form.title" type="text" id="title" name="title"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            placeholder="Enter election title">
        </div>
        <div class="mb-4">
          <label for="scheduled_for" class="block text-gray-700 text-sm font-bold mb-2">Scheduled Date</label>
          <input 
            v-model="form.scheduled_for" type="date" id="scheduled_for" name="scheduled_for"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
        </div>
        <div class="mb-4">
          <label for="start_time" class="block text-gray-700 text-sm font-bold mb-2">Start Time</label>
          <input 
            v-model="form.start_time" type="time" id="start_time" name="start_time"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
        </div>
        <div class="mb-6">
          <label for="end_time" class="block text-gray-700 text-sm font-bold mb-2">End Time</label>
          <input 
            v-model="form.end_time" type="time" id="end_time" name="end_time"
            class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline">
        </div>
        <div class="flex items-center justify-between">
          <button
            @click="submitCreateElectionForm()"
            class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline cursor-pointer"
            type="button">
            Create Election
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
