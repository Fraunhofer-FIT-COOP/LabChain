import Vue from "vue";
import Vuex from "vuex";
import axios from "axios";

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
    createCase(context, payload) {
      return new Promise((resolve, reject) => {
        Vue.http
          .post(`http://127.0.0.1:5000/createCase`, {
            controller: payload["controller_name"]
              ? payload["controller_name"]
              : "controller",
            doctor: payload["dr_name"] ? payload["dr_name"] : "doctor",
            physician: payload["e_physician_name"]
              ? payload["e_physician_name"]
              : "physician",
            chef: payload["dpt_chief_name"]
              ? payload["dpt_chief_name"]
              : "chief"
          })
          .then(res => {
            resolve(res);
          })
          .catch(err => {
            reject(err);
          });
      });
    },
    sendRealDiagnosis(context, payload) {
      return new Promise((resolve, reject) => {
        Vue.http
          .post(`http://127.0.0.1:5000/sendRealDiagnosis`, {
            case_id: payload["case_id"] ? payload["case_id"] : "case_id",
            doctor: payload["doctor"] ? payload["doctor"] : "doctor",
            chief: payload["chief"] ? payload["chief"] : "chief",
            workflow_transaction: payload["workflow_transaction"]
              ? payload["workflow_transaction"]
              : "workflow_transaction",
            previous_transaction: payload["previous_transaction"]
              ? payload["previous_transaction"]
              : "previous_transaction",
            diagnosis: payload["diagnosis"] ? payload["diagnosis"] : "diagnosis"
          })
          .then(res => {
            resolve(res);
          })
          .catch(err => {
            reject(err);
          });
      });
    },
    showDiagnosisWithPhysicianID(context, payload) {
      return new Promise((resolve, reject) => {
        Vue.http
          .post(`http://127.0.0.1:5000/showDiagnosisWithPhysicianID`, {
            username: payload["username"] ? payload["username"] : "username"
          })
          .then(res => {
            resolve(res);
          })
          .catch(err => {
            reject(err);
          });
      });
    },
    showAllDiagnosis(context, payload) {
      return new Promise((resolve, reject) => {
        axios
          .post(`http://127.0.0.1:5000/showAllDiagnosis`, {
            username: payload["chief"] ? payload["chief"] : "chief"
          })
          .then(res => {
            resolve(res);
          })
          .catch(err => {
            reject(err);
          });
      });
    },
    sendAssumedDiagnosis(context, payload) {
      return new Promise((resolve, reject) => {
        axios
          .post(`http://127.0.0.1:5000/sendAssumedDiagnosis`, {
            case_id: payload["case_id"] ? payload["case_id"] : "case_id",
            doctor: payload["doctor"] ? payload["doctor"] : "doctor",
            physician: payload["physician"]
              ? payload["physician"]
              : "physician",
            workflow_transaction: payload["workflow_transaction"]
              ? payload["workflow_transaction"]
              : "workflow_transaction",
            previous_transaction: payload["previous_transaction"]
              ? payload["previous_transaction"]
              : "previous_transaction",
            diagnosis: payload["diagnosis"] ? payload["diagnosis"] : "diagnosis"
          })
          .then(res => {
            resolve(res);
          })
          .catch(err => {
            reject(err);
          });
      });
    },
    checkTasks(context, payload) {
      return new Promise((resolve, reject) => {
        axios
          .post(`http://127.0.0.1:5000/checkTasks`, {
            username: payload["username"] ? payload["username"] : "username"
          })
          .then(res => {
            resolve(res);
          })
          .catch(err => {
            reject(err);
          });
      });
    }
  }
});
