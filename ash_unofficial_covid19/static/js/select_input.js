function patientsSelectInput() {
  const patientsInput = document.getElementById('patients-csv-url')
  patientsInput.focus()
  patientsInput.select()
}
function medicalInstitutionsSelectInput() {
  const medicalInstitutionsInput = document.getElementById('medical-institutions-csv-url')
  medicalInstitutionsInput.focus()
  medicalInstitutionsInput.select()
}


document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("patients-csv-url").addEventListener("click", patientsSelectInput, false)
  document.getElementById("medical-institutions-csv-url").addEventListener("click", medicalInstitutionsSelectInput, false)
}, false)
