<template>
  <div class="hospital">
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
  </div>
</template>

<script>
export default {
  name: "hospital",
  data() {
    return {
      dr_name: "",
      e_physician_name: "",
      dpt_chief_name: ""
    };
  },
  mounted() {},
  methods: {
    createCase() {
      let payload = {
        dr_name: this.dr_name,
        e_physician: this.e_physician_name,
        dpt_chief: this.dpt_chief_name
      };
      this.$store.dispatch("createCaseDemo", payload);
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
