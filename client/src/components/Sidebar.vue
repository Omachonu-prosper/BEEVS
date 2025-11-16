<script setup>
const props = defineProps({
  currentSection: String
});

const emit = defineEmits(['section-change']);

const actions = ['Details', 'Posts', 'Candidates', 'Voters', 'Institutional records'];

const changeSection = (section) => {
  emit('section-change', section);
};
</script>

<template>
  <div class="w-64 bg-white p-4 h-screen pt-10">
    <ul>
      <li v-for="action in actions" :key="action" class="mb-2">
        <button 
          @click="changeSection(action)"
          :class="['w-full text-left p-3 rounded-lg transition-colors duration-300', {
            'bg-blue-600 text-white': currentSection === action,
            'text-gray-700 hover:bg-gray-200 hover:text-blue-600': currentSection !== action
          }]"
        >
          {{ action }}
        </button>
      </li>
    </ul>
  </div>
</template>
