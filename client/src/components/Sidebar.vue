<script setup>
const props = defineProps({
  currentSection: String
});

const emit = defineEmits(['section-change']);

const actions = ['Details', 'Admins', 'Posts', 'Candidates', 'Voters', 'Institutional records'];

const changeSection = (section) => {
  emit('section-change', section);
};
</script>

<template>
  <div class="w-64 p-4 h-screen pt-10">
    <ul>
      <li v-for="action in actions" :key="action" class="mb-2">
        <button 
          @click="changeSection(action)"
          :class="['cursor-pointer w-full text-left p-2 rounded', {
            'bg-blue-600 text-white': currentSection === action,
            'bg-gray-300 hover:bg-gray-400': currentSection !== action
          }]"
        >
          {{ action }}
        </button>
      </li>
    </ul>
  </div>
</template>
