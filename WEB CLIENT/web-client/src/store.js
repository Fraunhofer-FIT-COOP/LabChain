import Vue from "vue";
import Vuex from "vuex";

Vue.use(Vuex);

export default new Vuex.Store({
  state: {
    patientDiagnosisData: []
  },
  getters: {
    getPatientDiagnosisData: state => state.patientDiagnosisData
  },
  mutations: {
    setPatientDiagnosisData(state, data = []) {
      state.patientDiagnosisData = data;
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
        //backup of this unknown url
        //.post(`https://reqres.in/api/users`, [
        .post(`https://127.0.0.1:5000/createCase`, [
          {
            //name: payload.dr_name ? payload.dr_name : "default",
            //job: payload.e_physician ? payload.e_physician : "111"
            controller: payload["controller_name"] ? payload["controller_name"] : "controller",
            physician: payload["e_physician"] ? payload["e_physician"] : "physician",
            doctor: payload["dr_name"] ? payload["dr_name"] : "doctor",
            chef: payload["dpt_chief"] ? payload["dpt_chief"] : "chef"
          }
        ])
        .then(res => {
          console.log(res);
        });
    },
    requestPatientDiagnosisData({ commit }) {
      Vue.http
        .post(`http://localhost:5000/showAllDiagnosis`, [
          {
            username: "chef"
          }
        ])
        .then(response => {
          console.log(response);
          commit("setPatientDiagnosisData", response.body);
        });
    }
  }
});
