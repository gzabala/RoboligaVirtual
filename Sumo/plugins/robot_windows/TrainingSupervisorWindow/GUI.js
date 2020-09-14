

function openFile(input, validExtensions) {
  return new Promise((resolve, reject) => {
    input.onchange = function () {
      let file = input.files[0];
      input.value = null;
      if (file === undefined) {
        return reject(null);
      }
      if (!validExtensions.some(ext => file.name.endsWith(ext))) {
        return reject("Por favor seleccione un archivo de Python.");
      }

      let reader = new FileReader();
      reader.onload = function(e) {
        try {
          let contents = e.target.result;
          resolve(contents);
        } catch (err) {
          reject(err);
        }
      };
      reader.readAsText(file);
    };
    input.click();
  });
}

$("#load-red-controller-button").on("click", function () {
  let input = $(this).find("input").get(0);
  openFile(input, [".py"]).then(function (data) {
    loadController(0, data);
  }).catch(function (err) {
    console.error(err);
  });
});

$("#load-green-controller-button").on("click", function () {
  let input = $(this).find("input").get(0);
  openFile(input, [".py"]).then(function (data) {
    loadController(1, data);
  }).catch(function (err) {
    console.error(err);
  });
});

function loadController(id, code) {
  send(["loadController", id, code]);
}
