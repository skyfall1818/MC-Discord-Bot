async function login() {
    const user = document.getElementById('username').value;
    const pass = document.getElementById('password').value;
    
    if (!user) {
        statusArea.textContent = "Please enter a username";
        return
    }
    if (!user) {
        statusArea.textContent ="Please enter a password";
        return
    }

    const serverIp = '192.168.1.101';
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
                localStorage.setItem("loggedUser", user);
                localStorage.setItem("loggedPass", pass);
                
                // Move to the next page
                window.location.href = "dashboard.html";
            }
            else {
                statusArea.textContent = "Incorrect username or password";
            }
        } else {
            statusArea.textContent = 'Error sending message.';
        }
    } catch (error) {
        console.error('Error sending message:', error);
        statusArea.textContent = 'Error connecting to the server.';
    }

}