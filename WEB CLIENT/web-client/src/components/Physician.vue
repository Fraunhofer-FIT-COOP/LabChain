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
            <template slot="assumed_diagnosis" slot-scope="row">
              <b-form-input @change="inputValueChanged" placeholder="Enter your diagnosis">Update</b-form-input>
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
        <P>Total:{{totalOpenTasks}} </p>
      </b-col>
      <b-col sm="6" class="bottom-space doctor-form">
        <b-card-text>
          <b-table
            selectable
            :select-mode="selectMode"
            selectedVariant="success"
            :fields="tableTitleRight"
            :items="comparisonTaskData"
          ></b-table>
        </b-card-text>
         <P>Total:{{totalDiagnosisComparisions}} Right:{{totalTrueDiagnosis}} Wrong:{{totalTrueDiagnosis}} </p>
      </b-col>
    </b-row>
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
        { key: "workflow_id", label: "ID" },
        { key: "assumed_diagnosis", label: "Assumed Diagnosis" },
        { key: "real_diagnosis", label: "Real Diagnosis" }
      ],
      physicianOpenTaskData: [],
      comparisonTaskData: [],
      selectMode: "single",
      lastUpdatedDiagnosis: "single",
      updated_diagnosis_value: "",
      totalOpenTasks: 0,
      totalDiagnosisComparisions: 0,
      totalTrueDiagnosis: 0
    };
  },
  methods: {
    findDiagnosisData() {
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
              element.real_diagnosis = '<input type="text">';
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
      let payload = {
        username: this.physician_name
      };
      this.$store.dispatch("showDiagnosisWithPhysicianID", payload).then(
        response => {
          console.log("showDiagnosisWithPhysicianID: ", response.data);
          if (response.data && response.data.length > 0) {
            this.comparisonTaskData = response.data;
            this.totalDiagnosisComparisions = response.data.length;
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
      console.log(item, index);
      this.sendDiagnosisToServer(item, index);
    },
    sendDiagnosisToServer(data, index) {
      let payload = {
        case_id: data.workflow_id,
        physician: this.physician_name,
        doctor: data.receiver,
        workflow_transaction: data.previous_transaction_hash,
        previous_transaction: data.workflow_transaction_hash,
        diagnosis: this.updated_diagnosis_value
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
      console.log(e);
    },
    inputValueChanged(val) {
      console.log(val);
      this.updated_diagnosis_value = val;
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
