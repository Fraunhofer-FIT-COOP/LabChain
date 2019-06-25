<template>
  <div class="doctor">
    <b-card-text>
      <p>Send Diagnosis</p>
      <b-container fluid>
        <b-row class="hospital-tbl-row">
          <b-col sm="4">
            <label :for="`type-text`">Case ID:</label>
          </b-col>
          <b-col sm="5">
            <b-form-input v-model="caseID"></b-form-input>
          </b-col>
          <b-col cols="3"></b-col>
          <b-col sm="4">
            <label :for="`type-text`">Doctor Name:</label>
          </b-col>
          <b-col sm="5">
            <b-form-input v-model="dr_name"></b-form-input>
          </b-col>
          <b-col cols="3"></b-col>
          <b-col sm="4">
            <label :for="`type-text`">Diagnosis:</label>
          </b-col>
          <b-col sm="5">
            <b-form-input v-model="diagnosis"></b-form-input>
          </b-col>
          <b-col cols="3"></b-col>
        </b-row>
        <b-button variant="success" @click="sendDiagnosis()">Send</b-button>
      </b-container>
    </b-card-text>
  </div>
</template>

<script>
export default {
  name: "doctor",
  data() {
    return {
      caseID: "",
      dr_name: "",
      diagnosis: ""
    };
  },
  mounted() {},
  methods: {
    sendDiagnosis() {
      let payload = {
        caseID: this.caseID,
        dr_name: this.dr_name,
        diagnosis: this.diagnosis
      };
      //this.$store.dispatch("createCaseDemo", payload);
    }
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
