<script setup>
import { ref } from 'vue';
import SolarTrashBin2Bold from '~icons/solar/trash-bin-2-bold';
import Popup from '@/components/Popup.vue';

const showAddPostPopup = ref(false);
const newPostTitle = ref('');

const posts = ref([
  { id: 1, title: 'President', candidates: 3 },
  { id: 2, title: 'Vice President', candidates: 2 },
]);

const addPost = () => {
  // Logic to add a new post
  console.log(newPostTitle.value);
  showAddPostPopup.value = false;
  newPostTitle.value = '';
};
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-primary">Posts</h2>
      <button @click="showAddPostPopup = true" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg cursor-pointer transition-colors duration-300">Add Post</button>
    </div>
    <ul class="bg-white rounded-lg shadow-inner">
      <li v-for="post in posts" :key="post.id" class="flex items-center justify-between p-4 border-b border-neutral-200 last:border-b-0">
        <span class="text-lg text-neutral-700">{{ post.title }}</span>
        <div class="flex items-center">
          <span class="text-sm text-neutral-500 mr-4">{{ post.candidates }} candidates</span>
          <button class="text-red-500 hover:text-red-700 cursor-pointer">
            <solar-trash-bin-2-bold class="h-6 w-6" />
          </button>
        </div>
      </li>
    </ul>
    <Popup v-if="showAddPostPopup">
      <template #header>Add New Post</template>
      <template #body>
        <p class="text-sm text-neutral-500 mb-4">Enter the title of the new post.</p>
        <input v-model="newPostTitle" type="text" class="w-full px-4 py-3 bg-neutral-200 border border-neutral-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600" placeholder="Enter post title">
      </template>
      <template #footer>
        <button @click="addPost" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg mr-2 cursor-pointer transition-colors duration-300">Add</button>
        <button @click="showAddPostPopup = false" class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-3 px-6 rounded-lg cursor-pointer transition-colors duration-300">Cancel</button>
      </template>
    </Popup>
  </div>
</template>
