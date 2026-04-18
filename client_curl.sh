IP=192.168.1.101
port=5000
json_file=Test.json
curl -X POST http://$IP:$port/message \
    -H "Content-Type: application/json" \
    --data-binary @$json_file