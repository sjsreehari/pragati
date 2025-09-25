#!/bin/bash

echo "🚀 DPR Analysis Platform - Git Push Helper"
echo "=========================================="

# Add all changes
echo "📁 Adding all changes to git..."
git add .

# Check git status
echo "📊 Current git status:"
git status --short

# Commit changes
echo ""
read -p "✍️  Enter commit message: " commit_message
if [ -z "$commit_message" ]; then
    commit_message="Updated DPR Analysis Platform with modern UI and fixed CI/CD pipeline"
fi

echo "💾 Committing changes..."
git commit -m "$commit_message"

# Push to repository
echo "🌐 Pushing to repository..."
git push origin main

echo ""
echo "✅ Successfully pushed to repository!"
echo "🔍 Check your GitHub repository for CI/CD pipeline status"
echo "📊 Pipeline will run automatically and test all components"