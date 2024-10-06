---
Title: Geth and Prysm in Docker Compose
Date: 2024-10-06
Category: Software
Status: published
---

I'm getting back into hacking on Ethereum nodes. Some of my tests are RPC-heavy, so a local setup is required. This will also speed up development since requests remain in my local network. However, I haven't found an easy Docker Compose setup for running Geth and Prysm together.

```yaml
version: "3.8"

services:
  geth:
    image: ethereum/client-go:stable
    container_name: geth
    restart: unless-stopped
    ports:
      - 30303:30303
      - 30303:30303/udp
      - 8545:8545
      - 8546:8546
      - 8551:8551
    volumes:
      - /ethereum/execution:/root
    command:
      - --http
      - --http.api=eth,net,web3
      - --http.addr=0.0.0.0
      - --authrpc.addr=0.0.0.0
      - --authrpc.vhosts=*
      - --authrpc.jwtsecret=/root/jwt.hex
      - --authrpc.port=8551

  prysm:
    image: gcr.io/prysmaticlabs/prysm/beacon-chain
    container_name: prysm
    restart: unless-stopped
    volumes:
      - /ethereum/consensus:/data
    depends_on:
      - geth
    ports:
      - 4000:4000
      - 3500:3500
    command:
      - --accept-terms-of-use
      - --datadir=/data
      - --disable-monitoring
      - --rpc-host=0.0.0.0
      - --execution-endpoint=http://99.97.0.1:8551
      - --jwt-secret=/data/jwt.hex
      - --rpc-host=0.0.0.0
      - --rpc-port=4000
      - --grpc-gateway-corsdomain=*
      - --grpc-gateway-host=0.0.0.0
      - --grpc-gateway-port=3500
      - --min-sync-peers=7
      - --checkpoint-sync-url=https://mainnet.checkpoint.sigp.io
      - --genesis-beacon-api-url=https://mainnet.checkpoint.sigp.io

networks:
  default:
    ipam:
      driver: default
      config:
        - subnet: 99.97.0.0/16
```

The network configuration is required to set Prysm's execution endpoint to the Geth instance. The setup assumes two root paths are set on the server with approprivate permissions: `/ethereum/consensus` and `/ethereum/execution`. The JWT has been generated with openssl in the execution directory:

```
openssl rand -hex 32 | tr -d "\n" > /ethereum/execution/jwt.hex
```

Once set up, the Compose file can be pasted into Portainer for easy deployment. Have fun!
