
let state = {
	running: false,
	gameCount: 0,
	time: 0,
	scoreboard: {
		dirty: true,
		positions: []
	},
	robots: [
		{name: null, wins: 0, time: 0},
		{name: null, wins: 0, time: 0}
	]
};

//The total time at the start
var maxTime = 2.5 * 60;

function openFile(input, validExtensions) {
  return new Promise((resolve, reject) => {
    input.onchange = function () {
      let file = input.files[0];
      input.value = null;
      if (file === undefined) {
        return reject(null);
      }
      if (!validExtensions.some(ext => file.name.endsWith(ext))) {
        return reject("Por favor seleccione un archivo " + validExtensions.join(" o "));
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
  openFile(input, [".py"]).then(function (code) {
    send(["loadController", 0, code]);
  }).catch(function (err) {
		if (err) { alert(err); }
  });
});

$("#load-green-controller-button").on("click", function () {
  let input = $(this).find("input").get(0);
  openFile(input, [".py"]).then(function (code) {
    send(["loadController", 1, code]);
  }).catch(function (err) {
    if (err) { alert(err); }
  });
});

$("#start-button").on("click", function () {
	send(["start"]);
	state.running = true;
	update();
});

$("#next-button").on("click", function () {
	send(["next"]);
});

$("#stop-button").on("click", function () {
	send(["stop"]);
	state.running = false;
	update();
});

let dispatchTable = {
	alert: function (msg) {
		if (msg) { alert(msg); }
	},
	log: function (msg){
		if (msg) { console.log(msg); }
	},
	crash: function () { console.log("CRASH!"); },
	update: function (time, r0ts, r1ts) {
		state.time = time;
		state.robots[0].time = r0ts;
		state.robots[1].time = r1ts;
		update();
	},
	loadedController: function (id, name) {
		state.robots[id].name = name;
		state.robots[id].wins = 0;
		update();
	},
	gameEnd: function (winnerId) {
		state.gameCount++;
		let winner = state.robots[winnerId];
		if (winner) {
			winner.wins++;

			if (state.robots[0].wins > state.robots[1].wins) {
				state.scoreboard.positions = [0, 1];
			} else if (state.robots[1].wins > state.robots[0].wins) {
				state.scoreboard.positions = [1, 0];
			}
		}
		state.scoreboard.dirty = true;
		update();
		console.log(JSON.stringify(state));
	}
}

function update() {
	$("#load-red-controller-button").attr("disabled", state.running);
	$("#load-green-controller-button").attr("disabled", state.running);
	$("#start-button").attr("disabled", state.running);
	$("#next-button").attr("disabled", !state.running);
	$("#stop-button").attr("disabled", !state.running);

	$("#r0-name").text(state.robots[0].name || "None");
	$("#r1-name").text(state.robots[1].name || "None");

	$("#game-time").text(calculateTimeRemaining(state.time));
	$("#r0-time").text(calculateTime(state.robots[0].time));
	$("#r1-time").text(calculateTime(state.robots[1].time));

	if (state.scoreboard.dirty) {
		state.scoreboard.dirty = false;

		let $board = $("#scoreboard");
		$board.html("");

		$board
			.append($("<li>")
				.addClass("list-group-item")
				.addClass("list-group-item-info")
				.append($("<span>").text("Tabla de posiciones"))
				.append($("<span>")
					.addClass("float-right")
					.text("(Partidas : " + state.gameCount + ")")));

		var positions = state.scoreboard.positions.map(i => state.robots[i]);
		for (let i = 0; i < positions.length; i++) {
			let robot = positions[i];
			$board
				.append($("<li>")
					.addClass("list-group-item")
					.append($("<span>").text((i + 1).toString() + ". " + robot.name))
					.append($("<span>")
						.addClass("float-right")
						.text("(" + robot.wins + " / " + state.gameCount + ")")));
		}
	}
}

function calculateTimeRemaining(done){
	//Create the string for the time remaining (mm:ss) given the amount of time elapsed
	//Convert to an integer
	done = Math.floor(done);
	//Calculate number of seconds remaining
	var remaining = maxTime - done;
	//Calculate seconds part of the time
	var seconds = Math.floor(remaining % 60);
	//Calculate the minutes part of the time
	var mins = Math.floor((remaining - seconds) / 60);
	//Convert parts to strings
	mins = String(mins)
	seconds = String(seconds)

	//Add leading 0s if necessary
	for (var i = 0; i < 2 - seconds.length; i++){
		seconds = "0" + seconds;
	}

	for (var i = 0; i < 2 - mins.length ; i++){
		mins = "0" + mins;
	}

	//Return the time string
	return mins + ":" + seconds;
}

function calculateTime(done){
	done = Math.floor(done);
	//Calculate number of seconds remaining
	var remaining = done;
	//Calculate seconds part of the time
	var seconds = Math.floor(remaining % 60);
	//Calculate the minutes part of the time
	var mins = Math.floor((remaining - seconds) / 60);
	//Convert parts to strings
	mins = String(mins)
	seconds = String(seconds)

	//Add leading 0s if necessary
	for (var i = 0; i < 2 - seconds.length; i++){
		seconds = "0" + seconds;
	}

	for (var i = 0; i < 2 - mins.length ; i++){
		mins = "0" + mins;
	}

	//Return the time string
	return mins + ":" + seconds;
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

window.onload = function() {
	update();
	window.robotWindow = webots.window();
	window.robotWindow.setTitle('Entrenamiento');
	window.robotWindow.receive = receive;
};

function send(data) {
	window.robotWindow.send(data.join(","));
}
