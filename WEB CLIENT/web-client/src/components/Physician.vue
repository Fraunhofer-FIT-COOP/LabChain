<template>
  <div class="physician">
    <b-table
      selectable
      :select-mode="selectMode"
      selectedVariant="success"
      @row-clicked="rowClicked"
      :fields="tableTitle"
      :items="items"
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
  </div>
</template>

<script>
export default {
  name: "physician",
  data() {
    return {
      tableTitle: [
        { key: "id", label: "ID" },
        { key: "real_diagnosis", label: "Real Diagnosis" },
        { key: "assumed_diagnosis", label: "Assumed Diagnosis" },
        { key: "update_diagnosis", label: "Update Diagnosis" }
      ],
      items: [
        {
          id: "123",
          real_diagnosis: "True",
          assumed_diagnosis:
            '<input type="text" id=this.selectedIndex name="FirstName" value="Mickey">'
        },
        {
          id: "2323",
          real_diagnosis: "True",
          assumed_diagnosis:
            '<input type="text" name="FirstName" value="Mickey">'
        },
        {
          id: "898",
          real_diagnosis: "True",
          assumed_diagnosis:
            '<input type="text" name="FirstName" value="Mickey">'
        }
      ],
      selectMode: "single",
      lastUpdatedDiagnosis: "single",
    };
  },
  methods: {
    update_diagnosis(item, index, e) {
      this.$store.dispatch("requestPhysicianOpenTask");
    },
    rowClicked(item, index, e) {
      console.log(item);
      console.log(index);
      console.log(e);
    },
    inputValueChanged(val) {
      console.log(val);
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
