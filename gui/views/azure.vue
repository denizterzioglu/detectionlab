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
            // Form fields with sample inputs
            region: "germany",
            publicKeyName: "id_logger",
            publicKeyPath: "/home/user/.ssh/id_logger.pub",
            privateKeyPath: "/home/user/.ssh/id_logger.pub",
            ipWhitelist: '["***.***.***.***/**"]',
            workspaceKey: "",
            workspaceID: "",
            tenantID: "",
            clientID: "",
            clientSecret: ""
        };
    },
    methods: {
        generateJson() {
            const variablesJson = {
                region: this.region,
                publicKeyName: this.publicKeyName,
                publicKeyPath: this.publicKeyPath,
                privateKeyPath: this.privateKeyPath,
                ipWhitelist: this.ipWhitelist,
                workspaceKey: this.workspaceKey,
                workspaceID: this.workspaceID,
                tenantID: this.tenantID,
                clientID: this.clientID,
                clientSecret: this.clientSecret
            };

            // Send the JSON data to the server
            this.$api
                .post("/plugin/detectionlab/update-azure-variables", variablesJson)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                alert('Variables updated and scripts executed successfully.');
                toast({
                    message: "Variables written",
                    position: "bottom-right",
                    type: "is-success",
                    dismissible: true,
                    pauseOnHover: true,
                    duration: 2000,
                });
                } else {
                alert('An error occurred.');
                toast({
                message: "Error accessing API",
                position: "bottom-right",
                type: "is-warning",
                dismissible: true,
                pauseOnHover: true,
                duration: 2000,
            });
                }
            })
            .catch((error) => {
            console.error(error);
            toast({
                message: "Error writing variables",
                position: "bottom-right",
                type: "is-warning",
                dismissible: true,
                pauseOnHover: true,
                duration: 2000,
            });
            });
        }
    }
};
</script>
<template lang="pug">
.content
    hr
    h3 Azure Environment Configuration
    p Fill in the details below to provide the variables required for automating infrastructure deployment.
    hr
form
.field.mb-4
    .label-wrapper(style="display: flex; align-items: center;")
    label.label(style="line-height: 1.2; margin-top: 4px;") Region
    a(href="https://azure.microsoft.com/en-us/global-infrastructure/locations/", target="_blank", style="margin-left: 8px; color: inherit; text-decoration: none; vertical-align: middle;")
        span.info-icon(style="font-size: 1.2em; display: inline-block; vertical-align: middle;") ℹ️
    input.input(v-model="region", type="text", placeholder="Enter Azure region")

.field.mb-4
    span The following values must point to a valid keypair.
.field.mb-4
    label.label Public key name
    input.input(v-model="publicKeyName", type="text", placeholder="Enter public key name")
.field.mb-4
    label.label Public key path
    input.input(v-model="publicKeyPath", type="text", placeholder="Enter public key path")
.field.mb-4
    label.label Private key path
    input.input(v-model="privateKeyPath", type="text", placeholder="Enter private key path")
.field.mb-4
    span Replace the IP address below with the IP address(es) you'll be using to connect to DetectionLab.
.field.mb-4    
    label.label IP Whitelist 
    input.input(v-model="ipWhitelist", type="text", placeholder='["***.***.***.***/**"]')
.field.mb-4
    span Add your workspace key and ID if you want to use Azure Log Analytics and Azure Sentinel
.field.mb-4
    label.label Workspace key
    input.input(v-model="workspaceKey", type="text", placeholder="Enter workspace key")
.field.mb-4
    label.label Workspace ID
    input.input(v-model="workspaceID", type="text", placeholder="Enter workspace ID")
.field.mb-4
    label.label Tenant ID
    input.input(v-model="tenantID", type="text", placeholder="Enter tenant ID")
.field.mb-4
    label.label Client ID
    input.input(v-model="clientID", type="text", placeholder="Enter client ID")
.field.mb-4
    label.label Client Secret
    input.input(v-model="clientSecret", type="password", placeholder="Enter client secret")
button.button.is-primary.is-fullwidth(@click="generateJson")
    span.icon
    i.fas.fa-download
    span Generate Lab Environment    
</template>