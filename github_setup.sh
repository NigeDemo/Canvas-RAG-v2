#!/bin/bash
# GitHub setup commands
# Replace 'yourusername' with your actual GitHub username

echo "Setting up GitHub remote..."
git remote add origin https://github.com/yourusername/Canvas-RAG-v2.git

echo "Pushing to GitHub..."
git branch -M main
git push -u origin main

echo "Repository successfully pushed to GitHub!"
echo "Your project is now available at: https://github.com/yourusername/Canvas-RAG-v2"
