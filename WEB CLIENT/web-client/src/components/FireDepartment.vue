<template>
  <div class="fire-department">
    <div class="fire-department-search">
      <b-row class="fire-department-tbl-row">
        <b-col sm="4" class="bottom-space doctor-form">
          <label :for="`type-text`">Username</label>
        </b-col>
        <b-col sm="5" class="bottom-space doctor-form">
          <b-form-input v-model="chief_name"></b-form-input>
        </b-col>
        <b-col cols="3" class="bottom-space doctor-form">
          <b-button class="search-btn bottom-space" variant="info" @click="getData()">Get Data</b-button>
        </b-col>
      </b-row>
    </div>
    <b-table ref="table" :fields="tableTitle" :items="items"></b-table>
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
  name: "fire-department",
  data() {
    return{
      chief_name: "",
      dismissSecs: 2,
      dismissCountDown: 0,
      alertVariant: "success",
      alertMsg: "",
      tableTitle: [
        { key: "workflow_id", label: "ID" },
        { key: "real_diagnosis", label: "Real Diagnosis" },
        { key: "assumed_diagnosis", label: "Assumed Diagnosis" }
      ],
      items: []
    };
  },
  methods: {
    getData() {
      let payload = {
        chief: this.chief_name
      };
      this.$store.dispatch("showAllDiagnosis", payload).then(
        response => {
          this.items=response.data;
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

.fire-department-search{
  margin-bottom: 30px;
}
</style>
