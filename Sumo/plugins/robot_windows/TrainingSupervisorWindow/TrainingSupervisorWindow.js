let state = {
	gameCount: 0,
	robots: [
		{name: null, wins: 0},
		{name: null, wins: 0}
	]
};

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

let dispatchTable = {
	alert: function (msg) {
		if (msg) { alert(msg); }
	},
	log: function (msg){
		if (msg) { console.log(msg); }
	},
	startup: function () {},
	update: function () {},
	loadedController: function (id, name) {
		state.robots[id].name = name;
		state.robots[id].wins = 0;
		update();
	},
}

function update() {
	$("#game-count").text(state.gameCount);

	for (let i = 0; i < state.robots.length; i++) {
		let robot = state.robots[i];
		let name = robot.name;
		if (name) {
			$("#r" + i + "-name").text(name);
		}
	}

	
}

function receive (message) {
	let parts = message.split(",");
	if (parts.length == 0) return;
	let fn = dispatchTable[parts[0]];
	if (!fn) {
		console.error("Unknown message: " + parts[0]);
	} else {
		parts.shift();
		fn.apply(this, parts);
	}
}

window.onload = function(){
	window.robotWindow = webots.window();
	window.robotWindow.setTitle('Entrenamiento');
	window.robotWindow.receive = receive;
};

function send(data) {
	window.robotWindow.send(data.join(","));
}
