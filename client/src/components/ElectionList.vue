<script setup>
import { RouterLink } from 'vue-router';
const elections = ["NACOS Election 2025", "NACOS Election 2024"]
</script>

<template>
    <div class="container mx-auto p-8">
        <h1 v-if="elections.length > 0" class="text-2xl font-bold text-primary mb-8">
            Select an election below or create a new election
        </h1>

        <h1 v-else class="text-2xl font-bold text-primary mb-8">
            You do not have any elections. Create one to get started.
        </h1>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
            <RouterLink 
                v-for="(election, index) in elections" :key="index"
                :to="'/election/' + election"
                class="bg-white rounded-lg shadow-lg p-8 cursor-pointer hover:shadow-xl hover:border-blue-600 border-2 border-transparent transition-all duration-300 flex items-center justify-center">
                <h2 class="text-xl font-bold text-blue-600">{{ election }}</h2>
            </RouterLink>

            <RouterLink to="/create-election" class="bg-blue-600 hover:bg-blue-700 rounded-lg shadow-lg p-8 cursor-pointer hover:shadow-xl transition-all duration-300 flex items-center justify-center">
                <div class="text-5xl text-white">+</div>
            </RouterLink>
        </div>
    </div>
</template>
