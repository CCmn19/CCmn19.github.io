function SegundaPantalla() {
    // Mostrar datos en la segunda pantalla
    document.getElementById('inicio').classList.add('hidden');
    document.getElementById('opciones').classList('hidden');
  }

function irAIA() {
    document.getElementById('opciones').classList.add('hidden');
    document.getElementById('ia').classList.remove('hidden');
  }