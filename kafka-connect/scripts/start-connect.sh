#!/bin/bash

echo "Waiting for Kafka to be ready..."
cub kafka-ready 1 30 -b $CONNECT_BOOTSTRAP_SERVERS || exit 1

echo "Starting Kafka Connect with installed plugins..."
echo "Available connectors:"
ls -la /usr/share/confluent-hub-components/

# Run the original startup script
exec /etc/confluent/docker/run