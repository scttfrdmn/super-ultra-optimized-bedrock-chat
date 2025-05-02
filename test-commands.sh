#!/bin/bash
# Test commands for ultra-optimized-bedrock-chat

# Using AWS profile 'aws', specifying us-west-2 region
echo "Testing with AWS profile 'aws' in us-west-2 region:"
echo "ultra-bedrock-chat --profile aws --region us-west-2"
echo 
echo "This will:"
echo "1. Connect to AWS using the 'aws' profile credentials"
echo "2. Use the us-west-2 region for Bedrock services"
echo "3. List all available models with their status"
echo "4. Filter for Claude 3.7 models (type 'claude' or 'haiku' after model selection prompt)"
echo
echo "Expected interaction:"
echo "-------------------------"
echo "┌────────── Models ✓=Enabled ────────────┐"
echo "│ Alias         ID           Access       │"
echo "│ claude-haiku  anthropic... On-Demand  ✓ │"
echo "│ claude-sonnet anthropic... On-Demand  ✓ │"
echo "│ claude-opus   anthropic... On-Demand  ✓ │"
echo "└─────────────────────────────────────────┘"
echo
echo "Model (name/ID/ARN): claude-haiku"
echo "Using anthropic.claude-3-haiku-20240307:0 (exit/clear)"
echo
echo "You: Hello, how are you?"
echo 
echo "AI: I'm doing well, thank you for asking! How can I assist you today?"
echo "-------------------------"
echo
echo "To show all models including disabled ones:"
echo "ultra-bedrock-chat --profile aws --region us-west-2 --all"