import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    patientDiagnosisData: [],
    physicianOpenTask: [],
  },
  getters: {
    getPatientDiagnosisData: state => state.patientDiagnosisData,
    getPhysicianOpenTask: state => state.physicianOpenTask
  },
  mutations: {
    setPatientDiagnosisData(state, data = []) {
      state.patientDiagnosisData = data;
    },
    setPhysicianOpenTask(state, data = []) {
      state.physicianOpenTask = data;
    }
  },
  actions: {
    createCase({commit}, payload) {
      Vue.http
        .post(`api/article/countPerMonth`, [
          {
            dr_name: payload["dr_name"] ? payload["dr_name"] : "",
            e_physician: payload["e_physician"] ? payload["e_physician"] : "",
            dpt_chief: payload["dpt_chief"] ? payload["dpt_chief"] : ""
          }
        ])
        .promise.always(response => {
          console.log(response);
        });
    },
    createCaseDemo({commit},payload) {
      console.log(payload)
      Vue.http
        .post(`https://reqres.in/api/users`, [
          {
            name: payload.dr_name ? payload.dr_name : "default",
            job: payload.e_physician ? payload.e_physician : "111"
          }
        ])
        .then(res => {
          console.log(res);
        });
    },
    requestPatientDiagnosisData({ commit }) {
      Vue.http
        .get(`http://localhost:5000/show-all-diagnosis`)
        .then(response => {
          console.log(response);
          commit("setPatientDiagnosisData", response.body);
        });
    },
    requestPhysicianOpenTask({ commit }) {
      Vue.http.get(`http://localhost:5000/demo`).then(response => {
        console.log(response);
        commit("setPhysicianOpenTask", response.body);
      });
    }
  }
});
