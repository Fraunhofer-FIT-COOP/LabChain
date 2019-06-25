<template>
  <div class="fire-department">
    <b-table
      :fields="tableTitle"
      :items="items"
    ></b-table>
  </div>
</template>

<script>
export default {
  name: "fire-department",
  data() {
    return {
      tableTitle: [
        { key: "id", label: "ID" },
        { key: "real_diagnosis", label: "Real Diagnosis" },
        { key: "assumed_diagnosis", label: "Assumed Diagnosis" }
      ],
      items: [
        { id: "123", real_diagnosis: "True", assumed_diagnosis: "False" },
        { id: "123", real_diagnosis: "True", assumed_diagnosis: "False" },
        { id: "123", real_diagnosis: "True", assumed_diagnosis: "False" },
        { id: "123", real_diagnosis: "True", assumed_diagnosis: "False" },
        { id: "123", real_diagnosis: "True", assumed_diagnosis: "False" },
        { id: "123", real_diagnosis: "True", assumed_diagnosis: "False" },
        { id: "123", real_diagnosis: "True", assumed_diagnosis: "False" }
      ]
    };
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
