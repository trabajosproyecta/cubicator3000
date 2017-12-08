const input = document.querySelector('input');
const preview = document.querySelector('#preview');

const updateFileDisplay = () => {
    const file = input.files
    if(file.length === 0) {
        preview.textContent = 'No has elegido ningún archivo';
      } else {
          const text = preview.querySelector('h4')
          text.textContent = file[0].name
          document.querySelector('#cubicatebtn').style.display = 'inline';
      }
}


input.addEventListener('change', updateFileDisplay);

