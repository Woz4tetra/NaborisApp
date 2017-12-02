var arrow_keys = [33,34,35,36,37,38,39,40];

$(document).keydown(function(e) {
     var key = e.which;
      if($.inArray(key, arrow_keys) > -1) {
          e.preventDefault();
          return false;
      }
      return true;
});

// Only run what comes next *after* the page has loaded
addEventListener("DOMContentLoaded", function() {
    // Grab all of the elements with a class of command
    // (which all of the buttons we just created have)
    var commandButtons = document.querySelectorAll(".command_button");

    for (var i = 0; i < commandButtons.length; i++)
    {
        var button = commandButtons[i];

        // For each button, listen for the "click" event
        button.addEventListener("click", function(e) {
            // When a click happens, stop the button
            // from submitting our form (if we have one)
            e.preventDefault();

            var clickedButton = e.target;
            var command = clickedButton.value;

            requestCommand(command, clickedButton);
        });
    }
}, true);


var motors_moving = false;
var looking = false;
let default_speed = 75;
let default_lateral = 150;
var increment = 0;
let amount = 4;

document.onkeydown = checkKeyDown;
document.onkeyup = checkKeyUp;

function checkKeyDown(e) {
    e = e || window.event;

    if (e.keyCode == '38') {
        // up arrow
        requestCommand("d 0 " + limitSpeed(default_speed + increment));
        motors_moving = true;
        increment += amount;
    }
    else if (e.keyCode == '40') {
        // down arrow
        requestCommand("d 180 " + limitSpeed(default_speed + increment));
        motors_moving = true;
        increment += amount;
    }
    else if (e.keyCode == '37') {
       // left arrow
       requestCommand("l " + limitSpeed(default_speed + increment));
       motors_moving = true;
       increment += amount;
    }
    else if (e.keyCode == '39') {
       // right arrow
       requestCommand("r " + limitSpeed(default_speed + increment));
       motors_moving = true;
       increment += amount;
    }
    else if (e.keyCode == '87') {
        // w
       requestCommand("d 0 " + limitSpeed(default_speed + increment));
       motors_moving = true;
       increment += amount;
    }
    else if (e.keyCode == '83') {
        // s
       requestCommand("d 180 " + limitSpeed(default_speed + increment));
       motors_moving = true;
       increment += amount;
    }
    else if (e.keyCode == '68') {
        // d
       requestCommand("d 270 " + limitSpeed(default_lateral + increment));
       motors_moving = true;
       increment += amount;
    }
    else if (e.keyCode == '65') {
        // a
       requestCommand("d 90 " + limitSpeed(default_lateral + increment));
       motors_moving = true;
       increment += amount;
    }

    else if (e.keyCode == '79') {
        // o
        requestCommand("toggle lights", document.getElementById("toggle_lights_button"));
    }

    if (!looking)
    {
        if (e.keyCode == '73') {
            // i
            requestCommand("look up");
            looking = true;
        }
        else if (e.keyCode == '75') {
            // k
            requestCommand("look down");
            looking = true;
        }
        else if (e.keyCode == '74') {
            // j
            requestCommand("look left");
            looking = true;
        }
        else if (e.keyCode == '76') {
            // l
            requestCommand("look right");
            looking = true;
        }
    }
}

function limitSpeed(speed) {
    if (speed > 255) {
        speed = 255;
    }
    if (speed < 0) {
        speed = 0;
    }
    console.log(speed);
    return speed;
}

function checkKeyUp(e) {
    e = e || window.event;

    if (motors_moving) {
        motors_moving = false;
        increment = 0;
        requestCommand("s");
    }
    else if (looking) {
        requestCommand("look");
        looking = false;
    }
}


function requestCommand(command, clickedButton=null) {
    // Now we need to send the data to our server
    // without reloading the page - this is the domain of
    // AJAX (Asynchronous JavaScript And XML)
    // We will create a new request object
    // and set up a handler for the response
    var request = new XMLHttpRequest();
    request.onload = function() {

        if (request.responseText.length > 0) {
            // clickedButton.innerHTML = request.responseText;
            alert(request.responseText);
            // clickedButton.value <- change sent command
        }
    };

    // We point the request at the appropriate command
    username = "user"
    password = "something"
    request.open("PUT", "/cmd", true);


    request.setRequestHeader("Content-Type", "application/json");
    request.withCredentials = true;
    // request.setRequestHeader("Authorization", "Basic " + btoa(username + ":" + password));

    var json_request = JSON.stringify({command:command});
    console.log(json_request);

    // and then we send it off
    request.send(json_request);
}


function myInsertAndExecute(id, text)
{
    domelement = document.getElementById(id);
    domelement.innerHTML = text;
    var scripts = [];

    ret = domelement.childNodes;
    for (var i = 0; ret[i]; i++) {
      if (scripts && myNodeName(ret[i], "script") && (!ret[i].type || ret[i].type.toLowerCase() === "text/javascript")) {
            scripts.push(ret[i].parentNode ? ret[i].parentNode.removeChild(ret[i]) : ret[i]);
        }
    }

    for(script in scripts)
    {
      myEvalScript(scripts[script]);
    }
}
function myNodeName(elem, name) {
    return elem.nodeName && elem.nodeName.toUpperCase() === name.toUpperCase();
}

function myEvalScript(elem)
{
    data = (elem.text || elem.textContent || elem.innerHTML || "");

    var head = document.getElementsByTagName("head")[0] || document.documentElement;
    script = document.createElement("script");
    script.type = "text/javascript";
    script.appendChild(document.createTextNode(data));
    head.insertBefore(script, head.firstChild);
    head.removeChild(script);

    if (elem.parentNode) {
        elem.parentNode.removeChild(elem);
    }
}
