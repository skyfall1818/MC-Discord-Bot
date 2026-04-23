// Connect to the WebSocket server
const serverIp = document.getElementById('ip-text').value;
const ws_id = localStorage.getItem("ws_id")
const ws = new WebSocket('wss://'+ serverIp + ':5000/ws/' + ws_id + '?');
const headerLog = document.getElementById('console-meta');
ws.onopen = () => {
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
    logToConsole(Body, 'info');
    // Process your constant data here (e.g., updating UI)
};

// Handle errors
ws.onerror = (error) => {
    set_connection_status(false);
    console.error('WebSocket error:', error);
};

// Implement reconnection logic
ws.onclose = () => {
    console.log('Connection closed, attempting reconnect...');
    // Implement re-connection logic here (e.g., setTimeout)
};

