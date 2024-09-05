<script setup>
import { inject, ref } from "vue";
import { toast } from "bulma-toast";

const $api = inject("$api");
const labState = inject("labState"); // Inject global state for lab generation

const sshKey = ref(null); // Reference to hold the SSH key file

const form = ref({
  region: "germanywestcentral",
  publicKeyName: "id_logger",
  publicKeyValue: "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIOeeDuJNFgNkL6hdK45AQLcnsVl5bnVi8fTM147u/BR generated-by-azure",
  workspaceKey: "",
  workspaceID: "",
  tenantID: "10c04932-a7ec-4924-b5dd-3fe916e518fe",
  clientID: "6b318441-aa93-458b-96f1-2ba1c2896bd9",
  subscriptionID: "eb8d4547-b055-4f7a-a699-b5d7696020d2",
  clientSecret: "",
  ipWhitelist: '["80.156.43.31","46.128.83.135"]'
});

const handleFileUpload = (event) => {
  sshKey.value = event.target.files[0];
};

const generateJson = () => {
  let ipWhitelistParsed;

  try {
    ipWhitelistParsed = JSON.stringify(JSON.parse(form.value.ipWhitelist));
  } catch (e) {
    alert('Invalid IP Whitelist format. Please provide a valid JSON array.');
    return;
  }

  const formData = new FormData();

  // Append form data
  Object.keys(form.value).forEach((key) => {
    formData.append(key, form.value[key]);
  });

  // Append the SSH key file
  if (sshKey.value) {
    formData.append('ssh_key', sshKey.value);
  } else {
    alert("Please upload an SSH key file.");
    return;
  }

  $api.post("/plugin/detectionlab/update-azure-variables", formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
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

      // Update global state to indicate lab is generated
      labState.isLabGenerated = true;
      labState.generatedPlatform = 'Azure'; // Indicate platform

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
};
</script>

<style scoped>
.field {
  max-width: 500px;
  margin: 0 auto;
}
button {
  max-width: 500px;
  margin: 0 auto;
}
</style>

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
    input.input(v-model="form.region", type="text", placeholder="Enter Azure region")

  .field.mb-4
    .label-wrapper(style="display: flex; align-items: center;")
      span The following values must point to a valid keypair defined in Azure.
      a(href="https://portal.azure.com/#browse/Microsoft.Compute%2FsshPublicKeys", target="_blank", style="margin-left: 8px; color: inherit; text-decoration: none; vertical-align: middle;")
        span.info-icon(style="font-size: 1.2em; display: inline-block; vertical-align: middle;") ℹ️
  .field.mb-4
    label.label Public key name
    input.input(v-model="form.publicKeyName", type="text", placeholder="Enter public key name")
  .field.mb-4
    label.label Public key value
    input.input(v-model="form.publicKeyValue", type="text", placeholder="Enter public key value")
  .field.mb-4
    label.label Private Key Upload
    input.input(@change="handleFileUpload", type="file", placeholder="Upload SSH key")
  .field.mb-4
    span Replace the IP address below with the IP address(es) you'll be using to connect to DetectionLab.
  .field.mb-4    
    label.label IP Whitelist 
    input.input(v-model="form.ipWhitelist", type="text", placeholder='["***.***.***.***/**"]')
  .field.mb-4
    .label-wrapper(style="display: flex; align-items: center;")
      span The following values must point to a valid service principle defined in Azure's app registeration .
      a(href="https://portal.azure.com/#view/Microsoft_AAD_IAM/ActiveDirectoryMenuBlade/~/RegisteredApps", target="_blank", style="margin-left: 8px; color: inherit; text-decoration: none; vertical-align: middle;")
        span.info-icon(style="font-size: 1.2em; display: inline-block; vertical-align: middle;") ℹ️
  .field.mb-4
    label.label Subscription ID
    input.input(v-model="form.subscriptionID", type="text", placeholder="Enter subscription ID")
  .field.mb-4
    label.label Tenant ID
    input.input(v-model="form.tenantID", type="text", placeholder="Enter tenant ID")
  .field.mb-4
    label.label Client ID
    input.input(v-model="form.clientID", type="text", placeholder="Enter client ID")
  .field.mb-4
    label.label Client Secret
    input.input(v-model="form.clientSecret", type="password", placeholder="Enter client secret")

  button.button.is-primary.is-fullwidth(type="button" @click="generateJson")
    span.icon
      i.fas.fa-download
    span Generate Lab Environment
</template>
