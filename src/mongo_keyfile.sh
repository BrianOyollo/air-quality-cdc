#!/bin/bash
# create-keyfile.sh
# Creates a secure keyfile for MongoDB replica set authentication.

set -e  # exit on any error

KEYFILE_DIR="./src/mongodb-key"
KEYFILE_PATH="$KEYFILE_DIR/mongo-keyfile"

# 1. Create the directory if it doesn't exist
mkdir -p "$KEYFILE_DIR"

# 2. Generate a random 756-bit (94-byte) base64 key (recommended by MongoDB)
openssl rand -base64 756 > "$KEYFILE_PATH"

# 3. Set strict permissions so only the owner can read
chmod 400 "$KEYFILE_PATH"
