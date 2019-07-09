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
          <b-button
            class="search-btn bottom-space"
            variant="info"
            @click="getData()"
            >Get Data</b-button
          >
        </b-col>
      </b-row>
    </div>
    <b-table
      ref="table"
      :fields="tableTitle"
      :items="items"
      :sort-by.sync="sortBy"
      :sort-desc.sync="sortDesc"
      :tbody-tr-class="rowClass"
    ></b-table>
    <p>Total: {{ total }} Correct: {{ totalRight }}</p>
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
  name: "fire-department",
  data() {
    return {
      sortBy: "workflow_id",
      sortDesc: false,
      chief_name: "",
      dismissSecs: 2,
      dismissCountDown: 0,
      alertVariant: "success",
      alertMsg: "",
      tableTitle: [
        { key: "workflow_id", label: "ID", sortable: true },
        { key: "real_diagnosis", label: "Real Diagnosis" },
        { key: "assumed_diagnosis", label: "Assumed Diagnosis" }
      ],
      items: [],
      total: 0,
      totalRight: 0
    };
  },
  methods: {
    getData() {
      if (!this.chief_name) return;
      let payload = {
        chief: this.chief_name
      };
      this.$store.dispatch("showAllDiagnosis", payload).then(
        response => {
          this.items = response.data;
          this.total = this.items.length;
          this.totalRight = this.items.filter(
            res => res.real_diagnosis === res.assumed_diagnosis
          ).length;
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
    rowClass(item, type) {
      if (!item) return;
      if (item.real_diagnosis === item.assumed_diagnosis)
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

.fire-department-search {
  margin-bottom: 30px;
}
</style>
