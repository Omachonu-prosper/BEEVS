<script setup>
import { RouterLink } from 'vue-router';

defineProps({
  crumbs: {
    type: Array,
    required: true
  }
});
</script>

<template>
  <nav class="flex" aria-label="Breadcrumb">
    <ol class="inline-flex items-center space-x-1 md:space-x-3">
      <li v-for="(crumb, index) in crumbs" :key="index" class="inline-flex items-center">
        <div class="flex items-center">
          <svg v-if="index !== 0" class="w-6 h-6 text-neutral-400" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg"><path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd"></path></svg>
          <RouterLink :to="crumb.to" class="ml-1 text-sm font-medium text-neutral-700 hover:text-primary md:ml-2">{{ crumb.text }}</RouterLink>
        </div>
      </li>
    </ol>
  </nav>
</template>
