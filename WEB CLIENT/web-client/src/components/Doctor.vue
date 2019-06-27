<template>
  <div class="doctor">
    <b-card-text>
      <p class="doctor-send-diagnosis">Send Diagnosis</p>
      <b-container fluid>
        <b-row class="hospital-tbl-row">
          <b-col sm="4" class="bottom-space doctor-form">
            <label :for="`type-text`">Case ID:</label>
          </b-col>
          <b-col sm="5" class="bottom-space doctor-form">
            <b-form-input v-model="caseID"></b-form-input>
          </b-col>
          <b-col cols="3" class="bottom-space doctor-form"></b-col>
          <b-col sm="4" class="bottom-space doctor-form">
            <label :for="`type-text`">Doctor Name:</label>
          </b-col>
          <b-col sm="5" class="bottom-space doctor-form">
            <b-form-input v-model="dr_name"></b-form-input>
          </b-col>
          <b-col cols="3" class="bottom-space doctor-form"></b-col>
          <b-col sm="4" class="bottom-space doctor-form">
            <label :for="`type-text`">Workflow Transaction:</label>
          </b-col>
          <b-col sm="5" class="bottom-space doctor-form">
            <b-form-input v-model="workflow_transaction"></b-form-input>
          </b-col>
          <b-col cols="3" class="bottom-space doctor-form"></b-col>
          <b-col sm="4" class="bottom-space doctor-form">
            <label :for="`type-text`">Previous Transaction:</label>
          </b-col>
          <b-col sm="5" class="bottom-space doctor-form">
            <b-form-input v-model="previous_transaction"></b-form-input>
          </b-col>
          <b-col cols="3" class="bottom-space doctor-form"></b-col>
          <b-col sm="4" class="bottom-space doctor-form">
            <label :for="`type-text`">Diagnosis:</label>
          </b-col>
          <b-col sm="5" class="bottom-space doctor-form">
            <b-form-input v-model="diagnosis"></b-form-input>
          </b-col>
          <b-col cols="3" class="bottom-space doctor-form"></b-col>
        </b-row>
        <b-button class="send-btn bottom-space" variant="success" @click="sendDiagnosis()">Send</b-button>
      </b-container>
    </b-card-text>
    <b-alert
      class="alert"
      :show="dismissCountDown"
      dismissible
      :variant="alertVariant"
      @dismissed="dismissCountDown=0"
      @dismiss-count-down="countDownChanged"
    >{{ alertMsg }}</b-alert>
  </div>
</template>

<script>
export default {
  name: "doctor",
  data() {
    return {
      caseID: "",
      dr_name: "",
      chief_name: "",
      workflow_transaction: "",
      previous_transaction: "",
      diagnosis: "",
      dismissSecs: 2,
      dismissCountDown: 0,
      alertVariant: "success",
      alertMsg: ""
    };
  },
  mounted() {},
  methods: {
    sendDiagnosis() {
      let payload = {
        case_id: this.caseID,
        doctor: this.dr_name,
        chief: this.chief_name,
        workflow_transaction: this.workflow_transaction,
        previous_transaction: this.previous_transaction,
        diagnosis: this.diagnosis
      };
      this.$store.dispatch("sendRealDiagnosis", payload).then(
        response => {
          console.log(response);
          this.alertMsg = "Diagnosis is successfully updated.";
          this.showAlert("success");
        },
        error => {
          console.log(error);
          this.alertMsg = "Something went wrong.";
          this.showAlert("danger");
        }
      );
    },
    showAlert(alertType) {
      this.alertVariant = alertType;
      this.dismissCountDown = this.dismissSecs;
    },
    countDownChanged(dismissCountDown) {
      this.dismissCountDown = dismissCountDown;
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
.bottom-space {
  margin-bottom: 10px;
}
.send-btn {
  float: right;
}
.doctor-send-diagnosis {
  font-size: 20px;
  font-family: initial;
}
.doctor-form {
  text-align: left;
}

.alert {
  margin-top: 50px;
}
</style>
