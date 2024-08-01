<template lang="pug">
.content
    h2 DetectionLab
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

button.button.is-primary.is-fullwidth(@click.prevent="generateJson")
    span.icon
    i.fas.fa-download
    span Generate JSON and Download
</template>
    
    <script>
    export default {
      data() {
        return {
          // Form fields with sample inputs
          proxmoxHost: "192.168.1.1",
          proxmoxNode: "pve",
          proxmoxUsername: "root@pam",
          proxmoxPassword: "",
          proxmoxNetworkWithDhcpAndInternet: "vmbr0",
          provisioningMachineIp: "",
          proxmoxVmPool: "",
          proxmoxSkipTlsVerify: "true",
          proxmoxDiskStoragePool: "local-lvm",
          proxmoxDiskStorageType: "lvm-thin",
          proxmoxIsoStoragePool: "local"
        };
      },
      methods: {
        generateJson() {
          // Construct the variables JSON object
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
    
          // Convert JSON object to string
          const jsonString = JSON.stringify(variablesJson, null, 2);
    
          // Create a blob with the JSON string
          const blob = new Blob([jsonString], { type: "application/json" });
    
          // Create a link element and trigger the download
          const link = document.createElement("a");
          link.href = URL.createObjectURL(blob);
          link.download = "variables.json";
          link.click();
        
          // Cleanup
          URL.revokeObjectURL(link.href);
        }
      }
    };
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
    