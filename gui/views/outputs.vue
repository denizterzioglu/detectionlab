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

let labState = inject("labState");

const fetchTerraformOutput = async () => {
  try {
    if (labState.value.generatedPlatform == 'Azure') {
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
    if (labState.value.generatedPlatform == 'Azure') {
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
      // Update for Proxmox and further
    }
  } catch (error) {
    errorMessage.value = "Failed to delete lab";
    console.error(error);
  }
};

onMounted(() => {
  fetchTerraformOutput();
});
</script>

<template lang="pug">
div(v-if="labState.isLoading" class="loading") Lab is being generated...
div(v-else-if="labState.isGenerated" class="lab-container")
  h3.lab-title {{ labState.generatedPlatform }} Lab Environment Tools
  p.lab-region Region: {{ terraformOutputs.region }}
  hr

  button(@click="deleteLab" class="deprovision-button") Deprovision Lab Environment

  div.tool-section
    h4 Public IPs
    ul.public-ips
      li Domain Controller: {{ terraformOutputs.dcPublicIp }}
      li Logger: {{ terraformOutputs.loggerPublicIp }}
      li Windows 10: {{ terraformOutputs.win10PublicIp }}
      li Windows Event Forwarder: {{ terraformOutputs.wefPublicIp }}

  div.tool-section
    h4 Access Tools
    div.buttons-container
      button(@click="window.open(terraformOutputs.fleetUrl, '_blank')" class="button is-link") Open Fleet
      button(@click="window.open(terraformOutputs.guacamoleUrl, '_blank')" class="button is-link") Open Guacamole
      button(@click="window.open(terraformOutputs.splunkUrl, '_blank')" class="button is-link") Open Splunk
      button(@click="window.open(terraformOutputs.velociraptorUrl, '_blank')" class="button is-link") Open Velociraptor
div(v-else class="error")
  p {{ errorMessage }}
</template>

<style scoped>
.loading {
  text-align: center;
  font-size: 1.2em;
}

.error {
  color: red;
  text-align: center;
  font-size: 1.2em;
}

.lab-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
}

.lab-title {
  text-align: center;
  font-size: 1.6em;
  margin-bottom: 10px;
}

.lab-region {
  text-align: center;
  font-size: 1.2em;
  margin-bottom: 20px;
}

.deprovision-button {
  display: block;
  width: 100%;
  padding: 10px;
  background-color: #ff4d4f;
  color: white;
  border: none;
  border-radius: 5px;
  font-size: 1.2em;
  cursor: pointer;
  margin-bottom: 20px;
}

.deprovision-button:hover {
  background-color: #ff7875;
}

.tool-section {
  margin-bottom: 20px;
}

.public-ips {
  list-style: none;
  padding: 0;
}

.public-ips li {
  background-color: #00567e;
  margin: 5px 0;
  padding: 8px;
  border-radius: 5px;
}

.buttons-container {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

button {
  flex: 1 1 45%;
  padding: 10px;
  font-size: 1em;
  margin: 5px;
}
</style>
