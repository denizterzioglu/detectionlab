<script setup>
import { inject } from "vue";

const $api = inject("$api");
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
    
<script>
export default {
    inject: ["$api"],
    data() {
        return {
            platforms: [
                'Azure',
                'Proxmox'
            ],
            selectedPlatform: {},
            selectedPlatformPaw: ''
        };
    },
    methods: {
        
    }
};
</script>

<template lang="pug">
.content
    h2 DetectionLab
    p Automates the infrastructure deployment for a lab environment in currently Proxmox using Packer, Vagrant, Terraform, and Ansible
    hr
// Platform SELECTION

div.mb-6
    form
        #select-platform.field.has-addons
            label.label.mr-5 Select a Platform
            .control.is-expanded
                .select.is-small.is-fullwidth
                    select(v-on:change="selectPlatform()" v-model="selectedPlatformPaw")
                        option(value="" disabled selected) Select a platform
                        template(v-for="platform of platforms" :key="platform")
                            option(v-bind:value="platform" v-text="`${platform}`")

div.has-text-centered.content(v-show="!selectedPlatformPaw")
    p Select a platform to get started
</template>

