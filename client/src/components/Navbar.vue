<script setup>
import SolarPowerBold from '~icons/solar/power-bold'
import { useRouter } from 'vue-router'

const router = useRouter()

const logoutHandler = () => {
  router.push('/')
}
</script>

<template>
  <nav class="bg-white shadow-md">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <h1 class="text-2xl font-bold text-blue-600">BEEVS</h1>
          </div>
        </div>
        <div class="flex items-center">
          <div class="mr-4">
            <p class="text-sm text-gray-600">logged in as x@email.com</p>
            <p class="text-xs text-gray-500 text-right">super admin</p>
          </div>
          <button class="p-1 rounded-full text-gray-400 cursor-pointer  focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-gray-800 focus:ring-white">
            <span class="sr-only">Logout</span>
            <solar-power-bold class="text-blue-600 hover:color-blue-900" @click="logoutHandler()"/>
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>