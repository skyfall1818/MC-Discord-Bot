function SendErrorMessage(message) {
    const errorMessage = document.getElementById('error-message');
    errorMessage.textContent = message;
    errorMessage.style.display = 'contents';
}

async function login() {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    
    if (!user) {
        SendErrorMessage("Please enter a username");
        return
    }
    if (!pass) {
        SendErrorMessage("Empty password field");
        return
    }

    const serverIp = '192.168.1.100';
    const serverPort = '5000';
    const serverUrl = 'https://' + serverIp + ':' + serverPort + '/login';

    try {
        const response = await fetch(serverUrl, {
            method: 'POST', // Use POST method to send data in the body
            headers: {
                'Content-Type': 'application/json' // Indicate JSON data
            },
            body: JSON.stringify({ 
                user: user,
                pass: pass,
            }) // Send the data as a JSON string
        })

        console.log('Response:', response);
        if (response.ok) {
            const data = await response.json();
            if (data.reply == "Success") {
                // Store the variable
                token = data.token;
                ws_id = data.ws_id;
                localStorage.setItem("apiToken", token);
                localStorage.setItem("ws_id", ws_id);
                
                // Move to the next page
                window.location.href = "dashboard.html";
            }
            else {
                SendErrorMessage("Incorrect username or password");
            }
        } else {
            SendErrorMessage('Error sending message.');
        }
    } catch (error) {
        console.error('Error sending message:', error);
        SendErrorMessage('Error connecting to the server.');
    }

}