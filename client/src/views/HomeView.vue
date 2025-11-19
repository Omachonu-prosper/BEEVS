<script setup>
import { RouterLink } from 'vue-router';
</script>

<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-600 via-blue-700 to-indigo-800">
    <!-- Hero Section -->
    <div class="relative overflow-hidden">
      <!-- Background Pattern -->
      <div class="absolute inset-0 opacity-10">
        <div class="absolute transform rotate-45 -top-20 -right-20 w-96 h-96 bg-white rounded-full"></div>
        <div class="absolute transform -rotate-12 top-40 -left-20 w-72 h-72 bg-white rounded-full"></div>
        <div class="absolute transform rotate-12 bottom-20 right-40 w-64 h-64 bg-white rounded-full"></div>
      </div>

      <!-- Navigation Bar -->
      <nav class="relative z-10 container mx-auto px-6 py-6">
        <div class="flex justify-between items-center">
          <div class="flex items-center space-x-3">
            <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
              <svg class="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.012 4.536A9 9 0 1118 3.52"></path>
              </svg>
            </div>
            <span class="text-2xl font-bold text-white">BEEVS</span>
          </div>
          <RouterLink
            to="/login"
            class="bg-white text-blue-600 px-6 py-2 rounded-lg font-semibold hover:bg-gray-100 transition-colors duration-300 shadow-lg"
          >
            Admin Login
          </RouterLink>
        </div>
      </nav>

      <!-- Hero Content -->
      <div class="relative z-10 container mx-auto px-6 py-20 md:py-32">
        <div class="max-w-4xl mx-auto text-center">
          <h1 class="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Blockchain-Enabled<br />
            <span class="text-blue-200">Electronic Voting System</span>
          </h1>
          <p class="text-xl md:text-2xl text-blue-100 mb-12 max-w-3xl mx-auto">
            Secure, transparent, and tamper-proof elections powered by blockchain technology and facial recognition
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <RouterLink
              to="/login"
              class="bg-white text-blue-600 px-8 py-4 rounded-xl font-bold text-lg hover:bg-gray-100 transition-all duration-300 shadow-2xl hover:shadow-xl hover:scale-105"
            >
              Get Started
            </RouterLink>
            <a
              href="#features"
              class="bg-blue-500 bg-opacity-30 backdrop-blur-sm text-white border-2 border-white px-8 py-4 rounded-xl font-bold text-lg hover:bg-opacity-40 transition-all duration-300"
            >
              Learn More
            </a>
          </div>
        </div>
      </div>

      <!-- Stats Section -->
      <div class="relative z-10 container mx-auto px-6 pb-20">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-4xl mx-auto">
          <div class="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 text-center border border-white border-opacity-20">
            <div class="text-4xl font-bold text-black-100 mb-2">100%</div>
            <div class="text-blue-600 font-medium">Secure</div>
          </div>
          <div class="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 text-center border border-white border-opacity-20">
            <div class="text-4xl font-bold text-black-100 mb-2">24/7</div>
            <div class="text-blue-600 font-medium">Accessible</div>
          </div>
          <div class="bg-white bg-opacity-10 backdrop-blur-lg rounded-2xl p-8 text-center border border-white border-opacity-20">
            <div class="text-4xl font-bold text-black-100 mb-2">∞</div>
            <div class="text-blue-600 font-medium">Transparent</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Features Section -->
    <div id="features" class="bg-white py-20">
      <div class="container mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">Why Choose BEEVS?</h2>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Experience the future of democratic voting with cutting-edge technology
          </p>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <!-- Feature 1 -->
          <div class="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl p-8 hover:shadow-xl transition-shadow duration-300">
            <div class="w-14 h-14 bg-blue-600 rounded-xl flex items-center justify-center mb-6">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">Blockchain Security</h3>
            <p class="text-gray-600">
              Every vote is recorded on an immutable blockchain, ensuring complete transparency and preventing any tampering or fraud.
            </p>
          </div>

          <!-- Feature 2 -->
          <div class="bg-gradient-to-br from-green-50 to-emerald-50 rounded-2xl p-8 hover:shadow-xl transition-shadow duration-300">
            <div class="w-14 h-14 bg-green-600 rounded-xl flex items-center justify-center mb-6">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">Facial Recognition</h3>
            <p class="text-gray-600">
              Advanced AI-powered facial recognition ensures only authorized voters can cast their ballots, eliminating impersonation.
            </p>
          </div>

          <!-- Feature 3 -->
          <div class="bg-gradient-to-br from-purple-50 to-pink-50 rounded-2xl p-8 hover:shadow-xl transition-shadow duration-300">
            <div class="w-14 h-14 bg-purple-600 rounded-xl flex items-center justify-center mb-6">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">Full Transparency</h3>
            <p class="text-gray-600">
              Voters can audit their votes on the blockchain at any time, ensuring accountability and building trust in the process.
            </p>
          </div>

          <!-- Feature 4 -->
          <div class="bg-gradient-to-br from-orange-50 to-red-50 rounded-2xl p-8 hover:shadow-xl transition-shadow duration-300">
            <div class="w-14 h-14 bg-orange-600 rounded-xl flex items-center justify-center mb-6">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">Real-time Results</h3>
            <p class="text-gray-600">
              View election results as they happen with instant updates from the blockchain, no more waiting for manual counting.
            </p>
          </div>

          <!-- Feature 5 -->
          <div class="bg-gradient-to-br from-teal-50 to-cyan-50 rounded-2xl p-8 hover:shadow-xl transition-shadow duration-300">
            <div class="w-14 h-14 bg-teal-600 rounded-xl flex items-center justify-center mb-6">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.012 4.536A9 9 0 1118 3.52"></path>
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">One Person, One Vote</h3>
            <p class="text-gray-600">
              Smart contracts enforce voting rules automatically, preventing duplicate votes and ensuring election integrity.
            </p>
          </div>

          <!-- Feature 6 -->
          <div class="bg-gradient-to-br from-yellow-50 to-amber-50 rounded-2xl p-8 hover:shadow-xl transition-shadow duration-300">
            <div class="w-14 h-14 bg-yellow-600 rounded-xl flex items-center justify-center mb-6">
              <svg class="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
            </div>
            <h3 class="text-xl font-bold text-gray-900 mb-3">24/7 Accessibility</h3>
            <p class="text-gray-600">
              Vote anytime during the election period from any device with internet access, making voting more convenient than ever.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- How It Works Section -->
    <div class="bg-gradient-to-br from-gray-50 to-gray-100 py-20">
      <div class="container mx-auto px-6">
        <div class="text-center mb-16">
          <h2 class="text-4xl md:text-5xl font-bold text-gray-900 mb-4">How It Works</h2>
          <p class="text-xl text-gray-600 max-w-2xl mx-auto">
            Voting made simple with just a few steps
          </p>
        </div>

        <div class="max-w-4xl mx-auto">
          <div class="space-y-8">
            <!-- Step 1 -->
            <div class="flex gap-6 items-start">
              <div class="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                1
              </div>
              <div class="flex-1">
                <h3 class="text-2xl font-bold text-gray-900 mb-2">Register as a Voter</h3>
                <p class="text-gray-600 text-lg">
                  Election administrators register eligible voters with their institutional details and capture a reference photo for facial recognition.
                </p>
              </div>
            </div>

            <!-- Step 2 -->
            <div class="flex gap-6 items-start">
              <div class="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                2
              </div>
              <div class="flex-1">
                <h3 class="text-2xl font-bold text-gray-900 mb-2">Authenticate with Your Face</h3>
                <p class="text-gray-600 text-lg">
                  When it's time to vote, enter your registration number and use your device's camera to verify your identity through facial recognition.
                </p>
              </div>
            </div>

            <!-- Step 3 -->
            <div class="flex gap-6 items-start">
              <div class="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                3
              </div>
              <div class="flex-1">
                <h3 class="text-2xl font-bold text-gray-900 mb-2">Cast Your Vote</h3>
                <p class="text-gray-600 text-lg">
                  Review all candidates for each position and make your selections. Your votes are encrypted and recorded on the blockchain immediately.
                </p>
              </div>
            </div>

            <!-- Step 4 -->
            <div class="flex gap-6 items-start">
              <div class="flex-shrink-0 w-12 h-12 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold text-xl">
                4
              </div>
              <div class="flex-1">
                <h3 class="text-2xl font-bold text-gray-900 mb-2">Verify & Audit</h3>
                <p class="text-gray-600 text-lg">
                  After voting, you can audit your votes anytime by authenticating again. View your voting trail and verify transactions on the blockchain explorer.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- CTA Section -->
    <div class="bg-gradient-to-r from-blue-600 to-indigo-700 py-20">
      <div class="container mx-auto px-6 text-center">
        <h2 class="text-4xl md:text-5xl font-bold text-white mb-6">
          Ready to Transform Your Elections?
        </h2>
        <p class="text-xl text-blue-100 mb-10 max-w-2xl mx-auto">
          Join the future of democratic voting with BEEVS - where every vote counts and transparency is guaranteed.
        </p>
        <RouterLink
          to="/login"
          class="inline-block bg-white text-blue-600 px-10 py-4 rounded-xl font-bold text-lg hover:bg-gray-100 transition-all duration-300 shadow-2xl hover:shadow-xl hover:scale-105"
        >
          Get Started Now
        </RouterLink>
      </div>
    </div>

    <!-- Footer -->
    <footer class="bg-gray-900 text-gray-300 py-12">
      <div class="container mx-auto px-6">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div>
            <div class="flex items-center space-x-3 mb-4">
              <div class="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.012 4.536A9 9 0 1118 3.52"></path>
                </svg>
              </div>
              <span class="text-xl font-bold text-white">BEEVS</span>
            </div>
            <p class="text-gray-400">
              Blockchain-based Electronic Voting System - Making elections secure, transparent, and accessible.
            </p>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-4">Quick Links</h4>
            <ul class="space-y-2">
              <li>
                <RouterLink to="/login" class="hover:text-blue-400 transition-colors">Admin Login</RouterLink>
              </li>
              <li>
                <a href="#features" class="hover:text-blue-400 transition-colors">Features</a>
              </li>
              <li>
                <a href="#" class="hover:text-blue-400 transition-colors">Documentation</a>
              </li>
            </ul>
          </div>
          <div>
            <h4 class="text-white font-semibold mb-4">Technology</h4>
            <ul class="space-y-2 text-gray-400">
              <li>Ethereum Blockchain</li>
              <li>Smart Contracts</li>
              <li>Facial Recognition AI</li>
              <li>End-to-End Encryption</li>
            </ul>
          </div>
        </div>
        <div class="border-t border-gray-800 pt-8 text-center text-gray-500">
          <p>&copy; 2025 BEEVS. All rights reserved. Built for transparent democracy.</p>
        </div>
      </div>
    </footer>
  </div>
</template>