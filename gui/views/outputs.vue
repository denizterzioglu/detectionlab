<script setup>
import { ref, onMounted } from "vue";
import axios from "axios";

const terraformOutputs = ref({
  dcPublicIp: '',
  fleetUrl: '',
  guacamoleUrl: '',
  loggerPublicIp: '',
  region: '',
  splunkUrl: '',
  velociraptorUrl: '',
  wefPublicIp: '',
  win10PublicIp: ''
});

const isLoading = ref(true);
const errorMessage = ref(null);

// Fetch the Terraform output from the backend
const fetchTerraformOutput = async () => {
  try {
    const response = await axios.get("/api/detectionlab/terraform-output");
    terraformOutputs.value = response.data;
    isLoading.value = false;
  } catch (error) {
    errorMessage.value = "Failed to load data";
    console.error(error);
  }
};

onMounted(() => {
  fetchTerraformOutput();
});
</script>

<template>
  <div v-if="isLoading" class="loading">Loading Terraform output...</div>

  <div v-else-if="errorMessage" class="error">
    <p>{{ errorMessage }}</p>
  </div>

  <div v-else>
    <h3>Lab Environment Tools</h3>
    <p>Region: {{ terraformOutputs.region }}</p>
    <hr>
    
    <div class="tool-section">
      <h4>Public IPs</h4>
      <ul>
        <li>Domain Controller: {{ terraformOutputs.dcPublicIp }}</li>
        <li>Logger: {{ terraformOutputs.loggerPublicIp }}</li>
        <li>Windows 10: {{ terraformOutputs.win10PublicIp }}</li>
        <li>Windows Event Forwarder: {{ terraformOutputs.wefPublicIp }}</li>
      </ul>
    </div>
    
    <div class="tool-section">
      <h4>Access Tools</h4>
      <button @click="window.open(terraformOutputs.fleetUrl, '_blank')" class="button is-link">Open Fleet</button>
      <button @click="window.open(terraformOutputs.guacamoleUrl, '_blank')" class="button is-link">Open Guacamole</button>
      <button @click="window.open(terraformOutputs.splunkUrl, '_blank')" class="button is-link">Open Splunk</button>
      <button @click="window.open(terraformOutputs.velociraptorUrl, '_blank')" class="button is-link">Open Velociraptor</button>
    </div>
  </div>
</template>

<style scoped>
.loading {
  text-align: center;
  font-size: 1.2em;
}

.error {
  color: red;
}

.tool-section {
  margin-bottom: 20px;
}

button {
  margin: 5px;
}
</style>
