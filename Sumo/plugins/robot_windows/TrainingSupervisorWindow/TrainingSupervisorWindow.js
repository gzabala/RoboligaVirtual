
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
		if (id == 0) {
			$("#r0-name").text(name);
		} else if (id == 1) {
			$("#r1-name").text(name);
		}
	},
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
