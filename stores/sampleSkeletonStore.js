import { defineStore } from "pinia";

export const useSampleDetectionLabStore = defineStore({
  id: "detectionlab",
  state: () => ({
    sampleStoreVariable: "Original Store Variable"
  }),
  actions: {
    changeStoreVariable(){
        this.sampleStoreVariable = "Store variable changed!";
    },
  },
});
