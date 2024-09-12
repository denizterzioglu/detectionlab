<script setup>
import { provide, inject, ref } from "vue";
import proxmox from './proxmox.vue';
import azure from './azure.vue';
import outputs from './outputs.vue';

const platforms = ['Azure', 'Proxmox'];
const selectedPlatform = ref('');
const $api = inject("$api");

const labState = ref({
    isLoading: false,
    isGenerated: false,
    generatedPlatform: '',
  });

const fetchLabState = async () => {
  try {
    const response = await $api.get("/plugin/detectionlab/get-state");
    labState.value = response.data;
  } catch (error) {
    console.error("Failed to fetch lab state:", error);
  }
};

fetchLabState();
provide("labState", labState);
</script>

<style scoped>
.field {
    max-width: 500px;
    margin: 0 auto;
}
button{
    max-width: 500px;
    margin: 0 auto;
}
</style>

<template lang="pug">
.content
    h2 DetectionLab
    p Automates the infrastructure deployment for a lab environment using Packer, Vagrant, Terraform, and Ansible
    hr

// Show different content based on global state
div(v-if="!labState.isGenerated && !labState.isLoading") 
    div.mb-6
        form
            #select-platform.field.has-addons
                label.label.mr-5(style="margin-top: 4px;")  Select a Platform
                .control.is-expanded
                    .select.is-small.is-fullwidth
                        select(v-model="selectedPlatform")
                            option(value="" disabled selected) Select a platform
                            template(v-for="platform of platforms" :key="platform")
                                option(v-bind:value="platform" v-text="`${platform}`")
    div.has-text-centered.content(v-show="!selectedPlatform")
        p Select a platform to get started

    div(v-show="selectedPlatform === 'Proxmox'")
        proxmox
    div(v-show="selectedPlatform === 'Azure'")
        azure

div(v-else)
    outputs
</template>
    