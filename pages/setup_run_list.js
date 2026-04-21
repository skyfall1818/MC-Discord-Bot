function logToConsole(message, type = "system"){
    const line = document.createElement("div")
    const consoleScroller = document.getElementById("console-scroller")
    line.className = `output-console__line output-console__line--${type}`
    const timestamp = new Date().toLocaleTimeString([], { hour12: false, hour: "2-digit", minute: "2-digit", second: "2-digit" })
    line.innerHTML = `<span style="color: #475569">[${timestamp}]</span> ${message}`
    try{
        consoleScroller.appendChild(line)
        consoleScroller.scrollTop = consoleScroller.scrollHeight
    }catch(e){
        console.log(e)
    }
}

function set_connection_status(status){
    const statusIndicator = document.getElementById('status-pulse');
    const statusText = document.getElementById('status-text');
    if (status){
        statusIndicator.className = `api-control-panel__pulse api-control-panel__pulse_success`;
        statusText.textContent = "Online";
    }
    else{
        statusIndicator.className = `api-control-panel__pulse api-control-panel__pulse_fail`;
        statusText.textContent = "Offline";
    }
}

async function sendRequest(message){
    const serverIp = '192.168.1.100';
    const serverPort = '5000';
    const serverUrl = 'https://' + serverIp + ':' + serverPort + '/request';
    const token = localStorage.getItem("apiToken");
    try {
        const response = await fetch(serverUrl, {
            method: 'POST', // Use POST method to send data in the body
            headers: {
                'Content-Type': 'application/json' // Indicate JSON data
            },
            body: JSON.stringify({ 
                token: token,
                message: message
            }) // Send the data as a JSON string
        })

        console.log('Response:', response);
        if (response.ok) {
            set_connection_status(true);
            const data = await response.json();
            return data.reply;
        } else {
            set_connection_status(false);
            logToConsole('Error receiving response.', 'error');
        }
    } catch (error) {
        set_connection_status(false);
        logToConsole('Error sending message: ' + error, 'error');
    }
    return '';
}

async function getGameList() {
    const gameListDropdown = document.getElementById('game-list-dropdown');
    const statusText = document.getElementById('status-pulse');
    const statusIndicator = document.getElementById('stataus-text');
    const api_message = 'run'

    const reply = await sendRequest(api_message);
    if (reply == '') {
        try{
            logToConsole('Error! could not retreive game list.', 'error');
        }catch(e){
            console.log(e);
        }
        return;
    }

    const game_list = String(reply).split('\n');
    if (game_list == '') {

    }
    for (let i = 0; i < game_list.length; i++) {
        if (game_list[i] == '') {
            continue;
        }
        info_list = game_list[i].split(':');
        const option = new Option(info_list[1], info_list[1]);
        option.value = info_list[0];
        gameListDropdown.add( option );
    }
    logToConsole('Game list updated.', 'success');
    
}
getGameList();