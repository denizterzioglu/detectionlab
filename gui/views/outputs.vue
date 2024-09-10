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

const $api = inject("$api");
const labState = inject("labState");

const errorMessage = ref(null);

// Fetch the Terraform output from the backend
const fetchTerraformOutput = async () => {
  try {
    if (labState.generatedPlatform == "Azure") {
      const response = await $api.get("/api/detectionlab/azure-terraform-output");
      terraformOutputs.value = response.data;
      isLoading.value = false;
    }
  } catch (error) {
    errorMessage.value = "Failed to load data";
    console.error(error);
  }
};

onMounted(() => {
  fetchTerraformOutput();
});
</script>

<template lang="pug">
  div(v-if="labState.isLoading" class="loading") Loading Terraform output...
  
  div(v-else-if="errorMessage" class="error")
    p {{ errorMessage }}

  div(v-else)
    h3 {{ labState.generatedPlatform }}Lab Environment Tools
    p Region: {{ terraformOutputs.region }}
    hr

    div.tool-section
      h4 Public IPs
      ul
        li Domain Controller: {{ terraformOutputs.dcPublicIp }}
        li Logger: {{ terraformOutputs.loggerPublicIp }}
        li Windows 10: {{ terraformOutputs.win10PublicIp }}
        li Windows Event Forwarder: {{ terraformOutputs.wefPublicIp }}

    div.tool-section
      h4 Access Tools
      button(@click="window.open(terraformOutputs.fleetUrl, '_blank')" class="button is-link") Open Fleet
      button(@click="window.open(terraformOutputs.guacamoleUrl, '_blank')" class="button is-link") Open Guacamole
      button(@click="window.open(terraformOutputs.splunkUrl, '_blank')" class="button is-link") Open Splunk
      button(@click="window.open(terraformOutputs.velociraptorUrl, '_blank')" class="button is-link") Open Velociraptor
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
