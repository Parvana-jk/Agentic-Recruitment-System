#!/bin/bash

# Start the Ollama server in the background
ollama serve &

# Wait for the server to be ready
echo "Waiting for Ollama server to start..."
until wget -q --spider http://localhost:11434; do
    sleep 2
done
echo "Ollama server is running. Starting model..."

# Run the model
ollama pull nomic-embed-text

ollama pull llama3.1 

tail -f /dev/null