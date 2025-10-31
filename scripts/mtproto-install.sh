#!/bin/bash

# Simple MTProto Proxy Docker Installation
# Based on LugoDev Medium article

set -e

# Create data directory if it doesn't exist
mkdir -p /opt/mtproto-proxy

# Run MTProto proxy container
docker run -d \
  --name mtproto-proxy \
  --restart always \
  -p 443:443 \
  -v /opt/mtproto-proxy:/data \
  telegrammessenger/proxy:latest