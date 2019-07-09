<template>
  <div class="doctor">
    <b-card-text>
      <p class="doctor-send-diagnosis"></p>
      <b-container fluid>
        <b-row class="hospital-tbl-row">
          <b-col sm="4" class="bottom-space doctor-form">
            <label :for="`type-text`">Doctor Name:</label>
          </b-col>
          <b-col sm="5" class="bottom-space doctor-form">
            <b-form-input v-model="dr_name"></b-form-input>
          </b-col>
          <b-col cols="3" class="bottom-space doctor-form">
            <b-button
              class="send-btn bottom-space"
              variant="success"
              @click="findDiagnosisData()"
              >FIND</b-button
            >
          </b-col>
        </b-row>

        <b-table
          selectable
          :select-mode="selectMode"
          selectedVariant="success"
          :fields="tableTitle"
          :items="taskData"
        >
          <template slot="real_diagnosis" slot-scope="data">
            <b-form-input
              v-model="data.item.real_diagnosis"
              placeholder="Enter your diagnosis"
              >Update</b-form-input
            >
          </template>

          <template slot="update_diagnosis" slot-scope="row">
            <b-button
              size="sm"
              @click="update_diagnosis(row.item, row.index, $event.target)"
              class="mr-1"
              >Update</b-button
            >
          </template>
        </b-table>
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
      alertMsg: "",
      tableTitle: [
        { key: "workflow_id", label: "ID" },
        { key: "timestamp", label: "Time" },
        { key: "real_diagnosis", label: "Real Diagnosis" },
        { key: "update_diagnosis", label: "Update Diagnosis" }
      ],
      taskData: [],
      selectMode: "single"
    };
  },
  mounted() {},
  methods: {
    findDiagnosisData() {
      if (!this.dr_name) return;
      this.checkMyTask();
    },
    sendDiagnosisToServer(data, index) {
      console.log(data);
      let payload = {
        case_id: data.workflow_id,
        doctor: this.dr_name,
        chef: data.receiver,
        workflow_transaction: data.workflow_transaction_hash,
        previous_transaction: data.previous_transaction_hash,
        diagnosis: data.real_diagnosis
      };
      this.$store.dispatch("sendRealDiagnosis", payload).then(
        response => {
          console.log(response);
          this.alertMsg = "Diagnosis is successfully updated.";
          this.showAlert("success");
          this.taskData.splice(index, 1);
        },
        error => {
          console.log(error);
          this.alertMsg = "Something went wrong.";
          this.showAlert("danger");
        }
      );
    },
    checkMyTask() {
      let payload = {
        username: this.dr_name
      };
      this.$store.dispatch("checkTasks", payload).then(
        response => {
          console.log("checkTasks: ", response.data);
          if (response.data) {
            response.data.forEach(element => {
              element.real_diagnosis = "";
              element.timestamp = this.formateDT(element.timestamp);
            });
            this.taskData = response.data;
          }
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
    },
    formateDT(timestamp) {
      let tm = parseInt(timestamp) * 1000;
      var date = new Date(tm);
      if (parseInt(timestamp) === 0) {
        return "- -";
      }
      var theyear = date.getFullYear();
      var themonth = this.addZero(date.getMonth() + 1);
      var thetoday = this.addZero(date.getDate());
      var hour = this.addZero(date.getHours());
      var minute = this.addZero(date.getMinutes());
      var sec = this.addZero(date.getSeconds());
      var formattedDT =
        thetoday +
        "." +
        themonth +
        "." +
        theyear +
        " " +
        hour +
        ":" +
        minute +
        ":" +
        sec;
      return formattedDT;
    },
    addZero(i) {
      if (i < 10) {
        i = "0" + i;
      }
      return i;
    },
    update_diagnosis(item, index, e) {
      console.log(item);
      this.sendDiagnosisToServer(item, index);
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
