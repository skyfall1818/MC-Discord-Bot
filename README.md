# Server

## Setting up Server

### generate SSL certificate (Self Sign)

1. Download **openssl**: ```https://slproweb.com/products/Win32OpenSSL.html```

2. Generate certificates:```openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes```

3. Move the certificates into websitebot/SSL

# Client

## Notes
Since the certificates are self signed, you will have to approve it by going to theri website

## test code

client_curl.sh