<script setup>
import { inject, ref, onMounted } from "vue";
import axios from "axios";
import { useDetectionLabStore } from "../../stores/detectionLabStore";

const detectionLabStore = useDetectionLabStore();
const $api = inject("$api");

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
const errorMessage = ref(null);

// Fetch the Terraform output from the backend
const fetchTerraformOutput = async () => {
  try {
    if (detectionLabStore.generatedPlatform == "Azure") {
      const response = await $api.get("/api/detectionlab/azure-terraform-output");
      terraformOutputs.value = response.data;
      isLoading.value = false;
    }
  } catch (error) {
    errorMessage.value = "Failed to load data";
    console.error(error);
  }
};

const deleteLab = async () => {
  try {
    if (detectionLabStore.generatedPlatform == 'Azure') {
      const response = await $api.get("/plugin/detectionlab/delete-azure-lab")
      const data = response.json()
      if (data.success) {
        alert('Lab was deprovisioned successfully.');
        toast({
          message: "Lab deprovisioned",
          position: "bottom-right",
          type: "is-success",
          dismissible: true,
          pauseOnHover: true,
          duration: 2000,
        });
        detectionLabStore.resetLabState()
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
    } else {
      detectionLabStore.resetLabState()
    }
    
  } catch (error) {
    errorMessage.value = "Failed to delete lab";
    console.error(error);
  }

}

onMounted(() => {
  fetchTerraformOutput();
});
</script>

<template lang="pug">
div(v-if="detectionLabStore.isLoading" class="loading") Lab is being generated...
div(v-else-if="errorMessage" class="error")
  p {{ errorMessage }}

div(v-else)
  h3 {{ selectedPlatform }}Lab Environment Tools
  p Region: {{ terraformOutputs.region }}
  hr

  button(@click="{{ deleteLab }}" class="button is-link") Delete Lab

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
