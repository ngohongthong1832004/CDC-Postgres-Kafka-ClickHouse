#!/usr/bin/env bash
#   Use this script to test if a given TCP host/port are available

WAITFORIT_host="$1"
WAITFORIT_port="$2"
shift 2
WAITFORIT_cmd="$@"

echo "⏳ Waiting for $WAITFORIT_host:$WAITFORIT_port..."

while ! nc -z "$WAITFORIT_host" "$WAITFORIT_port"; do
  sleep 1
done

echo "✅ $WAITFORIT_host:$WAITFORIT_port is available, starting command..."

exec $WAITFORIT_cmd
