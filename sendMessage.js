async function sendMessage() {
    const message = document.getElementById('messageInput').value;
    const statusArea = document.getElementById('statusArea');
    const serverIp = '192.168.1.101';
    const serverPort = '5000';
    // Replace with your server's actual HTTPS IP and endpoint
    const serverUrl = 'http://' + serverIp + ':' + serverPort + '/message';

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
        } else {
            statusArea.textContent = 'Error sending message.';
        }
    } catch (error) {
        console.error('Error sending message:', error);
        statusArea.textContent = 'Error connecting to the server.';
    }
}