/*
MainSupervisorWindow.js v2

Changelog:
 - Added human loaded indicator


Modified by Ricardo Moran and Gonzalo Zabala (CAETI - UAI)

*/


//The total time at the start
var maxTime = 2.5 * 60;

var visable = false;

var robot0Name = "Robot Rojo"
var robot1Name = "Robot Verde"

var robot0Loaded = false;
var robot1Loaded = false;

function receive (message){
	//Receive message from the python supervisor
	//Split on comma
	var parts = message.split(",");
	//If there is a message
	if (parts.length > 0){
		switch (parts[0]){
			case "alert":
				if (parts[1]) { alert(parts[1]); }
				break;
			case "startup":
				//Call for set up the robot window
				startup();
				break;
			case "update":
				//Update the information on the robot window every frame (of game time)
				update(parts.slice(1,parts.length + 1));
				break;
			case "loadedController":
				loadedController(parts[1], parts[2]);
				break;
			case "loadedProto":
				loadedProto(parts[1], parts[2]);
				break;
			case "lostJ1":
				lostJ1();
				break;
			case "lostJ2":
				lostJ2();
				break;
			case "draw":
				//The game is over
				draw();
				break;
			case "crash":
				crash();
				break;
			case "activityLoaded0":
				activityLoadedColor(0,parts[1],parts[2],parts[3])
				break;
			case "activityUnloaded0":
				activityUnloadedColour(0)
				break;
			case "activityLoaded1":
				activityLoadedColor(1,parts[1],parts[2],parts[3])
				break;
			case "activityUnloaded1":
				activityUnloadedColour(1)
				break;
			case "historyUpdate":
				let msg = message;
				let history0 = msg.split(",").slice(1,msg.length-1)
				updateHistory(history0)
				break;
			case "debug":
				window.robotWindow.setTitle(parts[1]);
				break;

		}
	}
}

function updateHistory(history0){
	let text = ""


	let history0End = false;

	let i = history0.length -1;


	while(!history0End){
		text += "<tr id='historyrow'>";
		if(history0[i] != null){
			text += "<div class='outerDiv'><div class='innerDiv'><td id='historyrowtext'>"+history0[i]+"</td></div></div>";
			i--;
		}else{
			text += "<div class='outerDiv'><div class='innerDiv'><td id='historyrowtext'></td></div></div>"
			history0End = true;
		}
		text += "</tr>";
	}
	document.getElementById("history").innerHTML = text;
}

function loadedController(id, name){
	//A controller has been loaded into a robot id is 0 or 1 and name is the name of the robot

	if (id == 0) {
		//Set name and toggle to unload button for robot 0
		document.getElementById("robot0Name").innerText = name;
		robot0Name = name;
		robot0Loaded = true;
	}
	if (id == 1) {
		//Set name and toggle to unload button for robot 1
		document.getElementById("robot1Name").innerText = name;
		robot1Name = name;
		robot1Loaded = true;
	}
}

function loadedProto(id, name){
	//A controller has been loaded into a robot id is 0 or 1 and name is the name of the robot

	if (id == 0){
		//Set name and toggle to unload button for robot 0
		document.getElementById("robot0Proto").innerText = name;
	}
	if (id == 1){
		//Set name and toggle to unload button for robot 1
		document.getElementById("robot1Proto").innerText = name;
	}
}

function startup (){
	//Turn on the run button and reset button when the program has loaded
	setEnableButton("runButton", true);
	setEnableButton("pauseButton", false);
	setEnableButton("resetButton", true);
}

function update (data){
	//Update the ui each frame of the simulation
	//Sets the scores and the timer
	document.getElementById("timer").innerHTML = calculateTimeRemaining(data[0]);
	document.getElementById("r0ts").innerHTML = calculateTime(data[1]);
	document.getElementById("r1ts").innerHTML = calculateTime(data[2]);
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
	//Create the string for the time remaining (mm:ss) given the amount of time elapsed
	//Convert to an integer
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

function runPressed(){
	//When the run button is pressed
	//Disable the run button
	setEnableButton("runButton", false);
	//Send a run command
	window.robotWindow.send("run");
	//Enable the pause button
	setEnableButton("pauseButton", true);
	//Disable all the loading buttons (cannot change loaded controllers once simulation starts)
	setEnableButton("loadController0", false);
	setEnableButton("loadController1", false);
	setEnableButton("loadRobot0", false);
	setEnableButton("loadRobot1", false);
}

function pausePressed(){
	//When the pause button is pressed
	//Turn off pause button, on run button and send signal to pause
	setEnableButton("pauseButton", false);
	window.robotWindow.send("pause");
	setEnableButton("runButton", true);
}

function resetPressed(){
	//When the reset button is pressed
	//Disable all buttons
	setEnableButton("runButton", false)
	setEnableButton("pauseButton", false);
	setEnableButton("resetButton", false);
	//Send signal to reset everything
	window.robotWindow.send("reset");
}

function loadController(robotNumber) {
	readFile().then(file => {
		if (!file.name.endsWith(".py")) {
			alert("El archivo no es un controlador válido");
		} else {
			let msg = ["loadController", robotNumber, file.name, file.contents].join(",");
			window.robotWindow.send(msg);
		}
	});
}

function loadRobot(robotNumber){
	readFile().then(file => {
		if (!file.name.endsWith(".json")) {
			alert("El archivo no es una definición de robot válida");
		} else {
			let msg = ["loadRobot", robotNumber, file.name, file.contents].join(",");
			window.robotWindow.send(msg);
		}
	});
}

function readFile() {
	return new Promise((res, rej) => {
		let input = document.getElementById("open-file-input");
		input.onchange = function () {
			let file = input.files[0];
			input.value = null;
			if (file == undefined) return res(null);

			let reader = new FileReader();
			reader.onload = function(e) {
				res({
					name: file.name,
					contents: e.target.result
				})
			};
			reader.readAsText(file);
		};
		input.click();
	});
}

function setEnableButton(name, state){
	//Set the disabled state of a button (state is if it is enabled as a boolean)
	document.getElementById(name).disabled = !(state);
}

//Set the onload command for the window
window.onload = function(){
	if (window.webots) {
		//Connect the window
		window.robotWindow = webots.window();
		//Set the title
		window.robotWindow.setTitle('Control de la Simulación');
		//Set which function handles the recieved messages
		window.robotWindow.receive = receive;
		//Set timer to inital time value
		document.getElementById("timer").innerHTML = calculateTimeRemaining(0);
	}
};

function endGame(){
	//Once the game is over turn off both the run and pause buttons
	setEnableButton("runButton", false)
	setEnableButton("pauseButton", false);

	if (!visable){
		show_winning_screen()
	}
}

function hide_winning_screen(){
	//Disable winner screen
	document.getElementById("winning-screen").style.display = "none";
}

function lostJ1() {
	document.getElementById("winning-team").innerText = "¡Ganó "+robot1Name+ "!"
	endGame();
}

function lostJ2() {
	document.getElementById("winning-team").innerText = "¡Ganó "+robot0Name+ "!"
	endGame();
}

function draw() {
	document.getElementById("winning-team").innerText = "¡Empate!"
	endGame();
}

function crash() {
	document.getElementById("winning-team").innerText = "Cancelado"
	endGame();
}

function calculateWinner(name0,name1){
	//if scores are the same
	if (scores[0] == scores[1]){
		//Show draw text
		document.getElementById("winning-team").innerText = "Draw!"
	}else {
		//Find index of highest scoring team

		if (scores[0] > scores[1]){
			//Show robot 0 win text
			document.getElementById("winning-team").innerText = name0 + " wins!"
		} else {
			//Show robot 1 win text
			document.getElementById("winning-team").innerText = name1 + " wins!"
		}
	}

}

function show_winning_screen(){

	//Show winning screen
  	document.getElementById("winning-screen").style.display = "inline-block";
  	visable = true;
}

function relocate(id){
	window.robotWindow.send("relocate,"+id.toString());
}
