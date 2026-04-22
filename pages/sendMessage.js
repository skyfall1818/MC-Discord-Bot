
async function sendMessage(message) {
    const serverIp = '192.168.1.100';
    const serverPort = '5000';
    const serverUrl = 'https://' + serverIp + ':' + serverPort + '/message';
    const user = localStorage.getItem("apiUser");
    const token = localStorage.getItem("apiToken");
    const ws_id = localStorage.getItem("ws_id");

    if (!message) {
        console.log('Message cannot be empty.');
        return;
    }

    try {
        const response = await fetch(serverUrl, {
            method: 'POST', // Use POST method to send data in the body
            headers: {
                'Content-Type': 'application/json' // Indicate JSON data
            },
            body: JSON.stringify({
                user: user,
                token: token,
                ws_id: ws_id,
                message: message
            }) // Send the data as a JSON string
        })

        console.log('Response:', response);
        if (response.ok) {
            const data = await response.json();
            logToConsole(data.reply, 'info');
        } else {
            logToConsole('Error sending message.', 'error');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        set_connection_status(false);
        logToConsole('Error sending message: ' + error, 'error');
    }
}