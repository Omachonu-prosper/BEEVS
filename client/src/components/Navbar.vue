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
      <div class="flex items-center justify-between h-20">
        <div class="flex items-center">
          <div class="flex-shrink-0">
            <h1 class="text-3xl font-bold text-primary">BEEVS</h1>
          </div>
        </div>
        <div class="flex items-center">
          <div class="mr-6">
            <p class="text-md text-neutral-700">logged in as omachonucodes@gmail.com</p>
            <p class="text-sm text-neutral-500 text-right">system admin</p>
          </div>
          <button class="p-2 rounded-full text-blue-600 hover:text-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-600">
            <span class="sr-only">Logout</span>
            <solar-power-bold class="h-7 w-7" @click="logoutHandler()"/>
          </button>
        </div>
      </div>
    </div>
  </nav>
</template>