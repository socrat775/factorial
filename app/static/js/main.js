function WebSocketConnect() {
    var ws = new WebSocket("ws://localhost:44434/factorial/?conn=websocket");
    window.ws = ws;

    ws.onopen = function() {
        console.log("Connection is opened");
        init();
    };

    ws.onmessage = function (evt) {
        var data = JSON.parse(evt.data);
        console.log("Message is received", data);

        if (data.status == "wait") {
            show_answer("wait...", true);
        } else if (data.status == "done") {
            show_answer("answer is "+ data.data, false);
        } else if (data.status == "error") {
            set_error(data.data);
        };
    };

    ws.onclose = function() { 
        ws.send(JSON.stringify({close: "close"}));
        document.cookie = '';
        console.log("Connection close");
    };

    // window.onbeforeunload = function(event) {
    //     console.log("onbeforeunload")
    //     socket.close();
    // };
};

function show_answer(msg, disap) {
    var p = document.createElement("p");
    p.setAttribute("id", "answer");
    p.innerHTML = msg;
    var area = document.getElementById("area");
    area.appendChild(p);
    if (disap) {
        setTimeout(
            function del_error(){
                area.removeChild(document.getElementById("answer"))
            },
            1700
        )
    };
};

function set_error(msg) {
    var p = document.createElement("p");
    p.setAttribute("id", "error");
    p.innerHTML = msg;
    var area = document.getElementById("area");
    area.appendChild(p);
    setTimeout(
        function del_error(){
            area.removeChild(document.getElementById("error"))
        },
        1700
    )
};

function init() {
    var input_text = document.createElement("input");
    input_text.setAttribute("type", "text");
    input_text.setAttribute("id", "number");

    var input_submit = document.createElement("input");
    input_submit.setAttribute("type","submit");
    input_submit.setAttribute("value","proc");
    input_submit.setAttribute("id", "proc_factorial");
    input_submit.onclick = function() {
        window.ws.send(
            JSON.stringify({
                status: "init",
                number: document.getElementById("number").value
            })
        );
    };
    var area = document.getElementById("area");
    area.appendChild(input_text);
    area.appendChild(input_submit);
};
