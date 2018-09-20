function myFunction () {
  var d = new Date()
  // var n = d.getTime()
  var sema = 'Semana '
  var hoy = new Date(d)
  hoy = new Date(hoy.getFullYear(), hoy.getMonth(), hoy.getDate())
  // domingo?
  if (hoy.getDay() === 0) {
    hoy.setDate(hoy.getDate() - 6)
  } else {
    hoy.setDate(hoy.getDate() - hoy.getDay() + 1)
  }
  sema += 'del lunes ' + hoy.toLocaleDateString()
  var cod = String(hoy.getTime())
  document.getElementById('semana').innerHTML = sema
  document.getElementById('codigo').innerHTML = cod.substring(4, cod.length - 5)
  cod.substring(4, cod.length - 5)
}
