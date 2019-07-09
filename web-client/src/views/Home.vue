<template>
  <div class="home">
    <b-container class="bv-example-row">
      <b-row>
        <b-col cols="12">
          <div>
            <b-card no-body>
              <b-tabs card>
                <b-tab title="Hospital" active>
                  <hospital></hospital>
                </b-tab>
                <b-tab title="Doctor">
                  <doctor></doctor>
                </b-tab>
                <b-tab title="Emergency Physician">
                  <physician></physician>
                </b-tab>
                <b-tab title="Fire Department">
                  <fire-department></fire-department>
                </b-tab>
              </b-tabs>
            </b-card>
          </div>
        </b-col>
      </b-row>
    </b-container>
  </div>
</template>

<script>
// @ is an alias to /src
import Doctor from "@/components/Doctor.vue";
import Hospital from "@/components/Hospital.vue";
import FireDepartment from "@/components/FireDepartment.vue";
import Physician from "@/components/Physician.vue";
//import Hello from "@/components/Hello.vue";
export default {
  name: "home",
  data() {
    return {};
  },
  mounted() {},
  methods: {},
  components: {
    Doctor,
    Hospital,
    FireDepartment,
    Physician
  }
};
</script>
