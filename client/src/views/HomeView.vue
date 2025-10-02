<script setup>
import { RouterLink } from 'vue-router';
</script>

<template>
    <h1>
        Welcome to BEEVS Please 
        <RouterLink to="/login" class="text-blue-500 hover:text-blue-700">
        login to your dashboard
        </RouterLink> or 
        <RouterLink to="/vote/test-vote" class="text-blue-500 hover:text-blue-700">
        View the vote page
        </RouterLink> or  <RouterLink to="/results/test-vote" class="text-blue-500 hover:text-blue-700">
        View election results
        </RouterLink>
    </h1>
</template>