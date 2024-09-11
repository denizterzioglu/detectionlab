<script setup>
import { provide, inject, ref, reactive, computed } from "vue";
import { useDetectionLabStore } from "../../stores/detectionLabStore";
import proxmox from './proxmox.vue';
import azure from './azure.vue';
import outputs from './outputs.vue';

const detectionLabStore = useDetectionLabStore();
const platforms = ['Azure', 'Proxmox'];

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
div(v-if="!detectionLabStore.isGenerated && !detectionLabStore.isLoading") 
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
    