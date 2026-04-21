async function sendMessage() {
    const message = document.getElementById('messageInput').value;
    const statusArea = document.getElementById('statusArea');
    const messageLog = document.getElementById('messages');
    messageLog.textContent = '';
    const serverIp = '192.168.1.101';
    const serverPort = '5000';
    const serverUrl = 'https://' + serverIp + ':' + serverPort + '/message';

    if (!message) {
        statusArea.textContent = 'Message cannot be empty.';
        return;
    }

    try {
        const response = await fetch(serverUrl, {
            method: 'POST', // Use POST method to send data in the body
            headers: {
                'Content-Type': 'application/json' // Indicate JSON data
            },
            body: JSON.stringify({ 
                name: "Test",
                description: "Test",
                message: message
            }) // Send the data as a JSON string
        })

        console.log('Response:', response);
        if (response.ok) {
            const data = await response.json();
            statusArea.textContent = data.reply;
            //connectToWebSocketServer('1234');
        } else {
            statusArea.textContent = 'Error sending message.';
        }
    } catch (error) {
        console.error('Error sending message:', error);
        statusArea.textContent = 'Error connecting to the server.';
    }
}

async function connectToWebSocketServer(WS_ID) {
    const messageLog = document.getElementById('messages');
    const ws = new WebSocket('wss://192.168.1.101:5000/ws/' + WS_ID + '?');
    ws.onopen = () => {
        /*const message = {
            method: 'GET', // Use POST method to send data in the body
            headers: {
                'Content-Type': 'application/json' // Indicate JSON data
            },
            body: JSON.stringify({ 
                data: 'Hello from the client!',
                WS_ID: '1234'
            })
        }*/
        console.log('Connected to server');
    };

    ws.onconnect = () => {
        console.log('Connected to server');
    };

    // Handle incoming messages
    ws.onmessage = (event) => {
        const data = event.data;
        console.log('Received:', data);
        messageLog.textContent = data;
        // Process your constant data here (e.g., updating UI)
    };

    // Handle errors
    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };

    // Implement reconnection logic
    ws.onclose = (event) => {
        const data = event.data;
        console.log('Received:', data);
        console.log('Connection closed');
        // Implement re-connection logic here (e.g., setTimeout)
    };
}

async function sendMessage(message) {
    const statusArea = document.getElementById('statusArea');
    const messageLog = document.getElementById('messages');
    messageLog.textContent = '';
    const serverIp = '192.168.1.101';
    const serverPort = '5000';
    const serverUrl = 'https://' + serverIp + ':' + serverPort + '/message';

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
                name: "Test",
                description: "Test",
                message: message
            }) // Send the data as a JSON string
        })

        console.log('Response:', response);
        if (response.ok) {
            const data = await response.json();
            statusArea.textContent = data.reply;
            //connectToWebSocketServer('1234');
        } else {
            statusArea.textContent = 'Error sending message.';
        }
    } catch (error) {
        console.error('Error sending message:', error);
        statusArea.textContent = 'Error connecting to the server.';
    }
}
