<script setup>
import { RouterLink } from 'vue-router';
const elections = ["NACOS Election 2025", "NACOS Election 2024"]
</script>

<template>
    <div class="container mx-auto mt-15 ">
        <h1 v-if="elections.length > 0" class="mb-5 text-lg">
            Select an election below or create a new election
        </h1>

        <h1 v-else class="mb-5 text-lg">
            You do not have any elections. Create one to get started.
        </h1>
        
        <div class="grid grid-cols-4 gap-3 lg:grid-cols-6">
            <RouterLink 
            v-for="(election, index) in elections" :key="index"
            :to="'/election/' + election"
            class="height-50 bg-gray-300 rounded-lg p-8 cursor-pointer hover:bg-gray-400">
                {{ election }}
            </RouterLink>

            <RouterLink to="/create-election" class="height-50 bg-gray-300 rounded-lg p-8 cursor-pointer hover:bg-gray-400">
                <div class="text-5xl text-center">+</div>
            </RouterLink>
        </div>
    </div>
</template>
