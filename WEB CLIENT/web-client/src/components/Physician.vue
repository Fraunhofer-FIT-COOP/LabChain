<template>
  <div class="physician">
    <b-row class="hospital-tbl-row">
      <b-col sm="4" class="bottom-space doctor-form">
        <label :for="`type-text`">Physician Name:</label>
      </b-col>
      <b-col sm="5" class="bottom-space doctor-form">
        <b-form-input v-model="physician_name"></b-form-input>
      </b-col>
      <b-col cols="3" class="bottom-space doctor-form">
        <b-button
          class="send-btn bottom-space"
          variant="success"
          @click="findDiagnosisData()"
        >Get Tasks</b-button>
        <b-button
          class="send-btn bottom-space"
          variant="success"
          @click="getCompareDiagnosisData()"
        >Compare Diagnosis</b-button>
      </b-col>
    </b-row>
    <b-row class="hospital-tbl-row">
      <b-col sm="6" class="bottom-space doctor-form">
        <b-card-text>
          <b-table
            selectable
            :select-mode="selectMode"
            selectedVariant="success"
            @row-clicked="rowClicked"
            :fields="tableTitle"
            :items="physicianOpenTaskData"
          >
            <template slot="assumed_diagnosis" slot-scope="data">
              <b-form-input
                v-model="data.item.assumed_diagnosis"
                placeholder="Enter your diagnosis"
              >Update</b-form-input>
            </template>

            <template slot="update_diagnosis" slot-scope="row">
              <b-button
                size="sm"
                @click="update_diagnosis(row.item, row.index, $event.target)"
                class="mr-1"
              >Update</b-button>
            </template>
          </b-table>
        </b-card-text>
        <p>Total:{{totalOpenTasks}}</p>
      </b-col>
      <b-col sm="6" class="bottom-space doctor-form">
        <b-card-text>
          <b-table
            selectable
            :select-mode="selectMode"
            selectedVariant="success"
            :fields="tableTitleRight"
            :tbody-tr-class="rowClass"
            :items="comparisonTaskData"
          ></b-table>
        </b-card-text>
        <p>Total:{{totalDiagnosisComparisions}} Right:{{totalTrueDiagnosis}}</p>
      </b-col>
    </b-row>
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
  name: "physician",
  data() {
    return {
      physician_name: "",
      tableTitle: [
        { key: "workflow_id", label: "ID" },
        { key: "timestamp", label: "Time" },
        { key: "assumed_diagnosis", label: "Assumed Diagnosis" },
        { key: "update_diagnosis", label: "Update Diagnosis" }
      ],
      tableTitleRight: [
        { key: "case_id", label: "ID" },
        { key: "assumed_diagnosis", label: "Assumed Diagnosis" },
        { key: "true_diagnosis", label: "Real Diagnosis" }
      ],
      physicianOpenTaskData: [],
      comparisonTaskData: [],
      selectMode: "single",
      lastUpdatedDiagnosis: "single",
      totalOpenTasks: 0,
      totalDiagnosisComparisions: 0,
      totalTrueDiagnosis: 0,
      dismissSecs: 2,
      dismissCountDown: 0,
      alertVariant: "success",
      alertMsg: ""
    };
  },
  methods: {
    findDiagnosisData() {
      if (!this.physician_name) return;
      this.checkMyTask();
    },
    checkMyTask() {
      let payload = {
        username: this.physician_name
      };
      this.$store.dispatch("checkTasks", payload).then(
        response => {
          console.log("checkTasks: ", response.data);
          if (response.data && response.data.length > 0) {
            response.data.forEach(element => {
              element.assumed_diagnosis = "";
              element.timestamp = this.formateDT(element.timestamp);
            });
            this.physicianOpenTaskData = response.data;
            this.totalOpenTasks = response.data.length;
          }
        },
        error => {
          console.log(error);
          this.alertMsg = "Something went wrong.";
          this.showAlert("danger");
        }
      );
    },
    getCompareDiagnosisData() {
      if (!this.physician_name) return;
      let payload = {
        username: this.physician_name
      };
      this.$store.dispatch("showDiagnosisWithPhysicianID", payload).then(
        response => {
          console.log("showDiagnosisWithPhysicianID: ", response.data);
          if (response.data && response.data.length > 0) {
            this.comparisonTaskData = response.data;
            this.totalDiagnosisComparisions = this.comparisonTaskData.length;
            this.totalTrueDiagnosis = this.comparisonTaskData.filter(
              res => res.assumed_diagnosis === res.true_diagnosis
            ).length;
          }
        },
        error => {
          console.log(error);
          this.alertMsg = "Something went wrong.";
          this.showAlert("danger");
        }
      );
    },
    update_diagnosis(item, index, e) {
      console.log(item);
      this.sendDiagnosisToServer(item, index);
    },
    sendDiagnosisToServer(data) {
      let payload = {
        case_id: data.workflow_id,
        physician: this.physician_name,
        doctor: data.receiver,
        workflow_transaction: data.workflow_transaction_hash,
        previous_transaction: data.previous_transaction_hash,
        diagnosis: data.assumed_diagnosis
      };
      console.log(payload);
      this.$store.dispatch("sendAssumedDiagnosis", payload).then(
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
    rowClicked(item, index, e) {
      console.log(item);
      console.log(index);
    },
    formateDT(timestamp) {
      var date = new Date(parseInt(timestamp));
      if (parseInt(timestamp) === 0) {
        return "- -" ;
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
    countDownChanged(dismissCountDown) {
      this.dismissCountDown = dismissCountDown;
    },
    showAlert(alertType) {
      this.alertVariant = alertType;
      this.dismissCountDown = this.dismissSecs;
    },
    rowClass(item, type) {
      if (!item) return;
      if (item.true_diagnosis === item.assumed_diagnosis)
        return "table-success";
      else return "table-danger";
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

.row.hospital-tbl-row {
  margin-bottom: 15px;
}

.bottom-space {
  margin-bottom: 10px;
}

.doctor-form {
  text-align: left;
}
</style>
