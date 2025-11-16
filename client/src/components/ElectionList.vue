<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { authFetch } from '@/utils/auth'

const elections = ref([])
const loading = ref(false)
const error = ref('')

async function loadElections() {
    loading.value = true
    error.value = ''
    try {
        const resp = await authFetch('/api/v1/elections')
        const json = await resp.json().catch(() => ({}))
        if (!resp.ok) {
            error.value = json?.message || 'Failed to load elections'
            return
        }
        // backend returns { elections: [...] }
        elections.value = json?.data?.elections || []
    } catch (err) {
        console.error(err)
        error.value = err?.message || 'Failed to load elections'
    } finally {
        loading.value = false
    }
}

onMounted(() => {
    loadElections()
})
</script>

<template>
    <div class="container mx-auto p-8">
        <h1 v-if="!loading && elections.length > 0" class="text-2xl font-bold text-primary mb-8">
            Select an election below or create a new election
        </h1>

        <h1 v-else-if="!loading && elections.length === 0" class="text-2xl font-bold text-primary mb-8">
            You do not have any elections. Create one to get started.
        </h1>

        <h1 v-else class="text-2xl font-bold text-primary mb-8">Loading elections...</h1>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-8">
            <RouterLink 
                v-for="(election, index) in elections" :key="election.id || index"
                :to="'/election/' + election.id"
                class="bg-white rounded-lg shadow-lg p-8 cursor-pointer hover:shadow-xl hover:border-blue-600 border-2 border-transparent transition-all duration-300 flex items-center justify-center">
                <h2 class="text-xl font-bold text-blue-600">{{ election.title }}</h2>
            </RouterLink>

            <RouterLink to="/create-election" class="bg-blue-600 hover:bg-blue-700 rounded-lg shadow-lg p-8 cursor-pointer hover:shadow-xl transition-all duration-300 flex items-center justify-center">
                <div class="text-5xl text-white">+</div>
            </RouterLink>
        </div>
    </div>
</template>
