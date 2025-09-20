<script setup>
const elections = ["NACOS Election 2025", "NACOS Election 2024"]
</script>

<template>
    <div class="container mx-auto mt-15 ">
        <h1 class="mb-5 text-lg">
            Select or create an election
        </h1>
        
        <div class="grid grid-cols-4 gap-3">
            <div 
            v-for="(election, index) in elections" :key="index"
            class="height-50 bg-gray-300 rounded-lg p-8 cursor-pointer hover:bg-gray-400">
                {{ election }}
            </div>

            <div class="height-50 bg-gray-300 rounded-lg p-8 cursor-pointer hover:bg-gray-400">
                <div class="text-5xl text-center">+</div>
            </div>
        </div>
    </div>
</template>
