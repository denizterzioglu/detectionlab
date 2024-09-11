<script setup>
import { inject, ref, onMounted } from "vue";
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
const errorMessage = ref(null);

let labState = inject("labState")

const fetchTerraformOutput = async () => {
  try {
    if (labState.generatedPlatform == "Azure") {
      const response = await $api.get("/plugin/detectionlab/azure-terraform-output");
      terraformOutputs.value = response.data;
    }
  } catch (error) {
    errorMessage.value = "Failed to load data";
    console.error(error);
  }
};

const deleteLab = async () => {
  try {
    if (labState.generatedPlatform == 'Azure') {
      const response = await $api.get("/plugin/detectionlab/delete-azure-lab");
      const data = await response.json();
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
      //Update for Proxmox and further
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
div(v-if="labState.isLoading" class="loading") Lab is being generated...
div(v-else-if="errorMessage" class="error")
  p {{ errorMessage }}

div(v-else)
  h3 {{ labState.generatedPlatform }}Lab Environment Tools
  p Region: {{ terraformOutputs.value.region }}
  hr

  button(@click="deleteLab") Deprovision Lab Environment

  div.tool-section
    h4 Public IPs
    ul
      li Domain Controller: {{ terraformOutputs.value.dcPublicIp }}
      li Logger: {{ terraformOutputs.value.loggerPublicIp }}
      li Windows 10: {{ terraformOutputs.value.win10PublicIp }}
      li Windows Event Forwarder: {{ terraformOutputs.value.wefPublicIp }}


  div.tool-section
    h4 Access Tools
    button(@click="window.open(terraformOutputs.value.fleetUrl, '_blank')" class="button is-link") Open Fleet
    button(@click="window.open(terraformOutputs.value.guacamoleUrl, '_blank')" class="button is-link") Open Guacamole
    button(@click="window.open(terraformOutputs.value.splunkUrl, '_blank')" class="button is-link") Open Splunk
      button(@click="window.open(terraformOutputs.value.velociraptorUrl, '_blank')" class="button is-link") Open Velociraptor
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
