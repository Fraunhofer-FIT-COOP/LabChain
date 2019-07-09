<template>
  <div>
    <b-table
      selectable
      :select-mode="selectMode"
      selectedVariant="success"
      :items="items"
      @row-selected="rowSelected"
    ></b-table>
    {{ selected }}
  </div>
</template>

<script>
export default {
  name: "hello",
  data() {
    return {
      items: [
        {
          isActive: true,
          age: 40,
          first_name: "Dickerson",
          last_name: "Macdonald"
        },
        { isActive: false, age: 21, first_name: "Larsen", last_name: "Shaw" },
        { isActive: false, age: 89, first_name: "Geneva", last_name: "Wilson" },
        { isActive: true, age: 38, first_name: "Jami", last_name: "Carney" }
      ],
      selectMode: "single",
      selected: []
    };
  },
  methods: {
    rowSelected(items) {
      this.selected = items;
    }
  }
};
</script>
