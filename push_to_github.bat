@echo off
echo [1/4] Initializing Git repository...
git init

echo [2/4] Adding files and committing...
git add .
git commit -m "Initial commit of candidate ranking system"
git branch -M main

echo [3/4] Adding GitHub remote...
git remote add origin https://github.com/vamsi-2003/data-ai-challenge.git

echo [4/4] Pushing to GitHub...
echo Please make sure you have created a public repository named "data-ai-challenge" at https://github.com/vamsi-2003
git push -u origin main

echo Push complete!
pause
