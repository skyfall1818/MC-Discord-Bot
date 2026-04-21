// Connect to the WebSocket server
const messageLog = document.getElementById('messages');
const headerLog = document.getElementById('header');
const ws = new WebSocket('wss://192.168.1.101:5000/ws/1234?');
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
    const output = JSON.parse(event.data);
    const Header = output.HEADER;
    const Body = output.MESSAGE;
    console.log('Received:', Header);
    headerLog.textContent = Header;
    messageLog.textContent += Body;
    // Process your constant data here (e.g., updating UI)
};

// Handle errors
ws.onerror = (error) => {
    console.error('WebSocket error:', error);
};

// Implement reconnection logic
ws.onclose = () => {
    console.log('Connection closed, attempting reconnect...');
    // Implement re-connection logic here (e.g., setTimeout)
};

