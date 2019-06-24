<template>
  <div class="home">
    <b-container class="bv-example-row">
      <b-row>
        <b-col cols="2"></b-col>
        <b-col cols="8">
          <div>
            <b-card no-body>
              <b-tabs card>
                <b-tab title="Hospital" active>
                  <b-card-text>
                    <p>Create Case</p>
                    <b-container fluid>
                      <b-row class="hospital-tbl-row">
                        <b-col sm="4">
                          <label :for="`type-text`">Doctor Name:</label>
                        </b-col>
                        <b-col sm="5">
                          <b-form-input v-model="dr_name"></b-form-input>
                        </b-col>
                        <b-col cols="3"></b-col>
                        <b-col sm="4">
                          <label :for="`type-text`">Physician Name:</label>
                        </b-col>
                        <b-col sm="5">
                          <b-form-input v-model="e_physician_name"></b-form-input>
                        </b-col>
                        <b-col cols="3"></b-col>
                        <b-col sm="4">
                          <label :for="`type-text`">Fire Dpt. Chief Name:</label>
                        </b-col>
                        <b-col sm="5">
                          <b-form-input v-model="dpt_chief_name"></b-form-input>
                        </b-col>
                        <b-col cols="3"></b-col>
                      </b-row>
                      <b-button variant="success" @click="createCase()">Create</b-button>
                    </b-container>
                  </b-card-text>
                </b-tab>
                <b-tab title="Doctor">
                  <b-card-text>Tab Contents 2</b-card-text>
                </b-tab>
                <b-tab title="Emergency Physician">
                  <b-card-text>Tab Contents 2</b-card-text>
                </b-tab>
                <b-tab title="Fire Department">
                  <b-card-text>Tab Contents 2</b-card-text>
                </b-tab>
              </b-tabs>
            </b-card>
          </div>
        </b-col>
        <b-col cols="2"></b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
// @ is an alias to /src
//import HelloWorld from "@/components/HelloWorld.vue";

export default {
  name: "home",
  data() {
    return {
      dr_name: "",
      e_physician_name: "",
      dpt_chief_name: ""
    };
  },
  mounted() {
    this.$store.dispatch("requestPatientDiagnosisData");
  },
  methods: {
    createCase() {
		let payload={
			dr_name:this.dr_name,
			e_physician: this.e_physician_name,
			dpt_chief: this.dpt_chief_name
		}
		console.log(payload)
		this.$store.dispatch("createCaseDemo",payload);
	}
  },
  components: {
    //HelloWorld
  }
};
</script>
