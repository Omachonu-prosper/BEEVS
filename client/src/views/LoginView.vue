<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { login as apiLogin, saveTokens } from '@/utils/auth'

const router = useRouter()

const form = reactive({
  email: "",
  password: ""
})

const loading = ref(false)
const error = ref('')

const submitLoginForm = async () => {
  error.value = ''
  loading.value = true
  try {
    const data = await apiLogin({ email: form.email, password: form.password })
    // data should include { admin, tokens }
    saveTokens(data.tokens, data.admin)
    router.push('/dashboard')
  } catch (err) {
    console.error(err)
    error.value = err?.message || 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen bg-neutral-100 flex items-center justify-center">
    <div class="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
      <h2 class="text-3xl font-bold text-center text-primary mb-8">Login to BEEVS</h2>
      <form @submit.prevent="submitLoginForm">
        <div class="mb-6">
          <label for="email" class="block text-neutral-700 text-sm font-bold mb-2">Email Address</label>
          <input 
            v-model="form.email" type="email" id="email" name="email"
            class="w-full px-4 py-3 bg-neutral-200 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Enter your email">
        </div>
        <div class="mb-6">
          <label for="password" class="block text-neutral-700 text-sm font-bold mb-2">Password</label>
          <input 
            v-model="form.password"
            type="password" id="password" name="password"
            class="w-full px-4 py-3 bg-neutral-200 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            placeholder="Enter your password">
        </div>
        <div class="flex items-center justify-between">
          <button
            type="submit"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-4 rounded-lg focus:outline-none focus:shadow-outline cursor-pointer transition-colors duration-300">
            Login
          </button>
        </div>
      </form>
    </div>
  </div>
</template>
