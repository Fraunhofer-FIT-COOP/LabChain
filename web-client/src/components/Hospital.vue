<template>
  <div class="hospital">
    <b-card-text>
      <p class="hospital-create-case">Create Case</p>
      <b-container fluid>
        <b-row class="hospital-tbl-row">
          <b-col sm="4" class="bottom-space hospital-form">
            <label :for="`type-text`">Controller Name:</label>
          </b-col>
          <b-col sm="5" class="bottom-space hospital-form">
            <b-form-input v-model="controller_name"></b-form-input>
          </b-col>
          <b-col cols="3" class="bottom-space"></b-col>
          <b-col sm="4" class="bottom-space hospital-form">
            <label :for="`type-text`">Doctor Name:</label>
          </b-col>
          <b-col sm="5" class="bottom-space hospital-form">
            <b-form-input v-model="dr_name"></b-form-input>
          </b-col>
          <b-col cols="3" class="bottom-space"></b-col>
          <b-col sm="4" class="bottom-space hospital-form">
            <label :for="`type-text`">Physician Name:</label>
          </b-col>
          <b-col sm="5" class="bottom-space hospital-form">
            <b-form-input v-model="e_physician_name"></b-form-input>
          </b-col>
          <b-col cols="3" class="bottom-space"></b-col>
          <b-col sm="4" class="bottom-space hospital-form">
            <label :for="`type-text`">Fire Dpt. Chief Name:</label>
          </b-col>
          <b-col sm="5" class="bottom-space hospital-form">
            <b-form-input v-model="dpt_chief_name"></b-form-input>
          </b-col>
          <b-col cols="3" class="bottom-space"></b-col>
        </b-row>
        <p v-if="caseIsCreated" class="caseIsCreated">Created case ID is</p>
        <b-button
          class="create-btn bottom-space"
          variant="success"
          @click="createCase()"
          >Create</b-button
        >
      </b-container>
    </b-card-text>
    <b-alert
      class="alert"
      :show="dismissCountDown"
      dismissible
      :variant="alertVariant"
      @dismissed="dismissCountDown = 0"
      @dismiss-count-down="countDownChanged"
      >{{ alertMsg }}</b-alert
    >
  </div>
</template>

<script>
export default {
  name: "hospital",
  data() {
    return {
      controller_name: "",
      dr_name: "",
      e_physician_name: "",
      dpt_chief_name: "",
      alertVariant: "success",
      alertMsg: "",
      caseIsCreated: false,
      dismissSecs: 5,
      dismissCountDown: 0
    };
  },
  mounted() {
    this.caseIsCreated = false;
  },
  methods: {
    createCase() {
      let payload = {
        controller_name: this.controller_name,
        dr_name: this.dr_name,
        e_physician_name: this.e_physician_name,
        dpt_chief_name: this.dpt_chief_name
      };
      this.$store.dispatch("createCase", payload).then(
        response => {
          console.log(response);
          this.alertMsg =
            "Case is successfully created. case ID: " +
            response.data["case_ID"];
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
.create-btn {
  float: right;
}
.caseIsCreated {
  float: left;
}
.hospital-create-case {
  font-size: 20px;
  font-family: initial;
}
.hospital-form {
  text-align: left;
}

.alert {
  margin-top: 50px;
}
</style>
