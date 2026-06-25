@echo off
set GIT="C:\Program Files\Git\cmd\git.exe"

echo [1/4] Initializing Git repository...
%GIT% init

echo [2/4] Adding files and committing...
%GIT% add .
%GIT% commit -m "Initial commit of candidate ranking system"
%GIT% branch -M main

echo [3/4] Adding GitHub remote...
rem Remove origin if it already exists, then add
%GIT% remote remove origin 2>nul
%GIT% remote add origin https://github.com/vamsi-2003/data-ai-challenge.git

echo [4/4] Pushing to GitHub (Force Overwriting remote defaults)...
%GIT% push -u origin main --force

echo Push complete!
