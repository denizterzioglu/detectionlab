<script setup>
import { inject, ref } from "vue";
import proxmox from './proxmox.vue';
import azure from './azure.vue';


const $api = inject("$api");
const platforms = ['Azure', 'Proxmox'];
const selectedPlatformPaw = ref('');
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
// Platform SELECTION

div.mb-6
    form
        #select-platform.field.has-addons
            label.label.mr-5 Select a Platform
            .control.is-expanded
                .select.is-small.is-fullwidth
                    select(v-model="selectedPlatformPaw")
                        option(value="" disabled selected) Select a platform
                        template(v-for="platform of platforms" :key="platform")
                            option(v-bind:value="platform" v-text="`${platform}`")

div.has-text-centered.content(v-show="!selectedPlatformPaw")
    p Select a platform to get started

div(v-show="selectedPlatformPaw === 'Proxmox'")
    proxmox
div(v-show="selectedPlatformPaw === 'Azure'")
    azure
</template>
