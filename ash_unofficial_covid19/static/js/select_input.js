function selectInput() {
  const input = document.getElementById('csv-url')
  input.focus()
  input.select()
}

document.addEventListener("DOMContentLoaded", function() {
  document.getElementById("csv-url").addEventListener("click", selectInput, false)
}, false)
