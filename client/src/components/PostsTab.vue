<script setup>
import { ref } from 'vue';
import { authFetch } from '@/utils/auth';
import { onMounted } from 'vue';
import SolarTrashBin2Bold from '~icons/solar/trash-bin-2-bold';
import Popup from '@/components/Popup.vue';

const props = defineProps({
  electionId: [String, Number]
});

const showAddPostPopup = ref(false);
const newPostTitle = ref('');

const posts = ref([]);
const loading = ref(false);
const error = ref('');

async function loadPosts() {
  loading.value = true;
  error.value = '';
  try {
    const resp = await authFetch(`/api/v1/elections/${props.electionId}/posts`);
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      error.value = json?.message || 'Failed to load posts';
      return;
    }
    posts.value = json?.data?.posts || [];
  } catch (err) {
    console.error(err);
    error.value = err?.message || 'Failed to load posts';
  } finally {
    loading.value = false;
  }
}

const addPost = async () => {
  try {
    const resp = await authFetch('/api/v1/posts', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title: newPostTitle.value, election_id: props.electionId })
    });
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      throw new Error(json?.message || 'Failed to add post');
    }
    showAddPostPopup.value = false;
    newPostTitle.value = '';
    await loadPosts();
  } catch (err) {
    console.error(err);
    error.value = err?.message || 'Failed to add post';
  }
};

onMounted(() => {
  if (props.electionId) loadPosts();
});

const deletingPostId = ref(null);
const confirmDeletePost = (postId) => {
  deletingPostId.value = postId;
  showDeleteConfirm.value = true;
};

const showDeleteConfirm = ref(false);

const deletePost = async () => {
  if (!deletingPostId.value) return;
  try {
    const resp = await authFetch(`/api/v1/posts/${deletingPostId.value}`, { method: 'DELETE' });
    const json = await resp.json().catch(() => ({}));
    if (!resp.ok) {
      throw new Error(json?.message || 'Failed to delete post');
    }
    showDeleteConfirm.value = false;
    deletingPostId.value = null;
    await loadPosts();
  } catch (err) {
    console.error(err);
    error.value = err?.message || 'Failed to delete post';
  }
};
</script>

<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h2 class="text-2xl font-bold text-primary">Posts</h2>
      <button @click="showAddPostPopup = true" class="bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-6 rounded-lg cursor-pointer transition-colors duration-300">Add Post</button>
    </div>
    <ul class="bg-white rounded-lg shadow-inner">
      <li v-if="loading" class="p-4">Loading posts...</li>
      <li v-else-if="error" class="p-4 text-red-600">{{ error }}</li>
      <li v-else-if="!loading && posts.length === 0" class="p-4 text-neutral-600">There are no posts for this election yet.</li>
      <li v-else v-for="post in posts" :key="post.id" class="flex items-center justify-between p-4 border-b border-neutral-200 last:border-b-0">
        <span class="text-lg text-neutral-700">{{ post.title }}</span>
        <div class="flex items-center">
          <span class="text-sm text-neutral-500 mr-4">{{ post.candidate_count || 0 }} candidates</span>
          <button @click.prevent="confirmDeletePost(post.id)" class="text-red-500 hover:text-red-700 cursor-pointer">
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

    <!-- Delete confirmation popup -->
    <Popup v-if="showDeleteConfirm">
      <template #header>Delete Post</template>
      <template #body>
        <p class="text-sm text-neutral-500 mb-4">Deleting this post will also delete all candidates associated with it. Are you sure?</p>
      </template>
      <template #footer>
        <button @click="deletePost" class="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-6 rounded-lg mr-2 cursor-pointer transition-colors duration-300">Delete</button>
        <button @click="() => { showDeleteConfirm = false; deletingPostId = null }" class="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-3 px-6 rounded-lg cursor-pointer transition-colors duration-300">Cancel</button>
      </template>
    </Popup>
  </div>
</template>
