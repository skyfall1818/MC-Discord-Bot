async function sendMessage() {
    const message = document.getElementById('messageInput').value;
    const statusArea = document.getElementById('statusArea');
    const serverIp = 'your-server-ip';
    const serverPort = 'port';
    // Replace with your server's actual HTTPS IP and endpoint
    const serverUrl = 'https://' + serverIp + ':' + serverPort + '/api/messages';

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
            body: JSON.stringify({ secureMessage: message }) // Send the data as a JSON string
        });

        if (response.ok) {
            const result = await response.json();
            statusArea.textContent = 'Message sent securely: ' + result.status;
        } else {
            statusArea.textContent = 'Failed to send message. Status: ' + response.status;
        }
    } catch (error) {
        console.error('Error sending message:', error);
        statusArea.textContent = 'Error connecting to the secure server.';
    }
}