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
            proxmoxHost: "10.0.0.76",
            proxmoxNode: "cli76",
            proxmoxUsername: "root@cli76",
            proxmoxPassword: "",
            proxmoxNetworkWithDhcpAndInternet: "vmbr0",
            provisioningMachineIp: "10.0.0.1",
            proxmoxVmPool: "",
            proxmoxSkipTlsVerify: "true",
            proxmoxDiskStoragePool: "local-lvm",
            proxmoxDiskStorageType: "lvm-thin",
            proxmoxIsoStoragePool: "local"
        };
    },
    methods: {
        generateJson() {
            const variablesJson = {
                proxmox_host: this.proxmoxHost,
                proxmox_node: this.proxmoxNode,
                proxmox_username: this.proxmoxUsername,
                proxmox_password: this.proxmoxPassword,
                proxmox_network_with_dhcp_and_internet: this.proxmoxNetworkWithDhcpAndInternet,
                provisioning_machine_ip: this.provisioningMachineIp,
                proxmox_vm_pool: this.proxmoxVmPool,
                proxmox_skip_tls_verify: this.proxmoxSkipTlsVerify,
                proxmox_disk_storage_pool: this.proxmoxDiskStoragePool,
                proxmox_disk_storage_type: this.proxmoxDiskStorageType,
                proxmox_iso_storage_pool: this.proxmoxIsoStoragePool
            };

            // Send the JSON data to the server
            this.$api
                .post("/plugin/detectionlab/update-proxmox-variables", variablesJson)
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
    h3 Proxmox Environment Configuration
    p Fill in the details below to generate the variables.json file required for automating infrastructure deployment.
    hr

form
.field.mb-4
    label.label Proxmox Host
    input.input(v-model="proxmoxHost", type="text", placeholder="Enter Proxmox Host IP")

.field.mb-4
    label.label Proxmox Node
    input.input(v-model="proxmoxNode", type="text", placeholder="Enter Proxmox Node")

.field.mb-4
    label.label Proxmox Username
    input.input(v-model="proxmoxUsername", type="text", placeholder="Enter Proxmox Username")

.field.mb-4
    label.label Proxmox Password
    input.input(v-model="proxmoxPassword", type="password", placeholder="Enter Proxmox Password")

.field.mb-4
    label.label Proxmox Network with DHCP and Internet
    input.input(v-model="proxmoxNetworkWithDhcpAndInternet", type="text", placeholder="Enter Network Interface")

.field.mb-4
    label.label Provisioning Machine IP
    input.input(v-model="provisioningMachineIp", type="text", placeholder="Enter Provisioning Machine IP")

.field.mb-4
    label.label Proxmox VM Pool
    input.input(v-model="proxmoxVmPool", type="text", placeholder="Enter VM Pool (Optional)")

.field.mb-4
    label.label Proxmox Skip TLS Verify
    input.input(v-model="proxmoxSkipTlsVerify", type="text", placeholder="Enter true or false")

.field.mb-4
    label.label Proxmox Disk Storage Pool
    input.input(v-model="proxmoxDiskStoragePool", type="text", placeholder="Enter Disk Storage Pool")

.field.mb-4
    label.label Proxmox Disk Storage Type
    input.input(v-model="proxmoxDiskStorageType", type="text", placeholder="Enter Disk Storage Type")

.field.mb-4
    label.label Proxmox ISO Storage Pool
    input.input(v-model="proxmoxIsoStoragePool", type="text", placeholder="Enter ISO Storage Pool")

button.button.is-primary.is-fullwidth(@click="generateJson")
    span.icon
    i.fas.fa-download
    span Generate JSON
</template>

