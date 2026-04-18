// Connect to the WebSocket server
const ws = new WebSocket('wss://your-websocket-url');

ws.onopen = () => {
    console.log('Connected to server');
};

// Handle incoming messages
ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Received:', data);
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