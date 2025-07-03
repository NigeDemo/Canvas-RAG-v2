# PowerShell script for Windows
# GitHub setup commands
# Replace 'yourusername' with your actual GitHub username
# For example: https://github.com/nige7/Canvas-RAG-v2.git

Write-Host "Setting up GitHub remote..." -ForegroundColor Green
git remote add origin https://github.com/NigeDemo/Canvas-RAG-v2.git

Write-Host "Pushing to GitHub..." -ForegroundColor Green
git branch -M main
git push -u origin main

Write-Host "Repository successfully pushed to GitHub!" -ForegroundColor Green
Write-Host "Your project is now available at: https://github.com/NigeDemo/Canvas-RAG-v2" -ForegroundColor Cyan
