<template>
  <div class="fixed inset-0 backdrop-blur-sm overflow-y-auto h-full w-full flex items-center justify-center">
    <div class="absolute inset-0 bg-gray-200 bg-opacity-75"></div>
    <div class="relative mx-auto p-8 border w-full max-w-lg shadow-lg rounded-2xl bg-white">
      <div class="text-center">
        <h3 class="text-2xl leading-6 font-bold text-gray-800 mb-4">
          <slot name="header"></slot>
        </h3>
        <div class="mt-4 px-7 py-3">
          <slot name="body"></slot>
        </div>
        <div class="items-center px-4 py-3">
          <slot name="footer"></slot>
        </div>
      </div>
    </div>
  </div>
</template>
