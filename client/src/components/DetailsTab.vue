  <script setup>
  import { ref, computed, onMounted } from 'vue'
  import { authFetch } from '@/utils/auth'

  const props = defineProps({
    electionId: { type: [String, Number], required: true }
  })

  const loading = ref(true)
  const election = ref({})

  function fmtDate(iso) {
    if (!iso) return '-'
    try {
      const d = new Date(iso)
      return d.toLocaleString()
    } catch (e) {
      return iso
    }
  }

  const formattedStartsAt = computed(() => fmtDate(election.value.starts_at))
  const formattedEndsAt = computed(() => fmtDate(election.value.ends_at))

  const status = computed(() => {
    const now = new Date()
    const starts = election.value.starts_at ? new Date(election.value.starts_at) : null
    const ends = election.value.ends_at ? new Date(election.value.ends_at) : null
    
    // If we have an end time and it has passed, election has ended
    if (ends && now > ends) return 'Ended'
    
    // If we have a start time and it hasn't arrived yet, election not started
    if (starts && now < starts) return 'Not started'
    
    // If we have a start time and we're past it (but before end or no end), in progress
    if (starts && now >= starts) return 'In progress'
    
    // Default: scheduled (no start/end times set)
    return 'Scheduled'
  })

  async function load() {
    loading.value = true
    try {
      const resp = await authFetch(`/api/v1/elections/${props.electionId}`)
      const json = await resp.json().catch(() => ({}))
      if (!resp.ok) {
        console.error('Failed to load election', json)
        election.value = {}
        return
      }
      election.value = json?.data?.election || {}
    } catch (err) {
      console.error('Error loading election', err)
      election.value = {}
    } finally {
      loading.value = false
    }
  }

  onMounted(() => {
    load()
  })
</script>


<template>
  <div>
    <h2 class="text-2xl font-bold text-primary mb-6">Election Data</h2>

    <div v-if="loading" class="py-6">
      <div class="text-sm text-neutral-500">Loading election details…</div>
    </div>

    <div v-else>
      <ul class="space-y-4">
        <li class="flex justify-between items-center pb-2 border-b border-neutral-200">
          <span class="font-semibold text-neutral-700">Title:</span>
          <span class="text-lg font-semibold text-primary">{{ election.title || '-' }}</span>
        </li>

        <li class="flex justify-between items-center pb-2 border-b border-neutral-200">
          <span class="font-semibold text-neutral-700">Status:</span>
          <span class="text-lg font-semibold text-primary">{{ status }}</span>
        </li>

        <li class="flex justify-between items-center pb-2 border-b border-neutral-200">
          <span class="font-semibold text-neutral-700">Starts at:</span>
          <span class="text-lg text-neutral-900">{{ formattedStartsAt }}</span>
        </li>

        <li class="flex justify-between items-center pb-2 border-b border-neutral-200">
          <span class="font-semibold text-neutral-700">Ends at:</span>
          <span class="text-lg text-neutral-900">{{ formattedEndsAt }}</span>
        </li>

        <li class="flex justify-between items-center pb-2 border-b border-neutral-200">
          <span class="font-semibold text-neutral-700">Candidates:</span>
          <span class="text-lg font-semibold text-neutral-900">{{ election.candidate_count ?? 0 }}</span>
        </li>

        <li class="flex justify-between items-center pb-2 border-b border-neutral-200">
          <span class="font-semibold text-neutral-700">Registered voters:</span>
          <span class="text-lg font-semibold text-neutral-900">{{ election.voter_count ?? 0 }}</span>
        </li>

        <li class="flex justify-between items-center pb-2 border-b border-neutral-200">
          <span class="font-semibold text-neutral-700">Cast votes:</span>
          <span class="text-lg font-semibold text-neutral-900">{{ election.cast_votes ?? 0 }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>