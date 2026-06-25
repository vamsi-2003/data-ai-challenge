@echo off
echo [1/4] Initializing Git repository...
git init

echo [2/4] Adding files and committing...
git add .
git commit -m "Initial commit of candidate ranking system"
git branch -M main

echo [3/4] Adding GitHub remote...
# Remove origin if it already exists, then add
git remote remove origin 2>nul
git remote add origin https://github.com/vamsi-2003/data-ai-challenge.git

echo [4/4] Pushing to GitHub (Force Overwriting remote defaults)...
git push -u origin main --force

echo Push complete!
pause
