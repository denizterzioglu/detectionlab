import { defineStore } from "pinia";

export const useDetectionLabStore = defineStore({
  id: "detectionlab",
  state: () => ({
    isLoading: false,
    isGenerated: false,
    generatedPlatform: null,
  }),
  actions: {
    setLoading(platform) {
      this.isLoading = true;
      this.generatedPlatform = platform;
    },
    setGenerated() {
      this.isGenerated = true;
      this.isLoading = false;
    },
    resetLabState() {
      this.isGenerated = false;
      this.generatedPlatform = null;
    }
  },
});
