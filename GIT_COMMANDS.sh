#!/bin/bash

# Initialize git repository (if not already done)
git init

# Add all files
git add .

# Commit with the message
git commit -F COMMIT_MESSAGE.txt

# Optional: Add remote and push
# git remote add origin <your-repo-url>
# git push -u origin main

echo "✅ Commit complete!"
echo ""
echo "To push to remote:"
echo "  git remote add origin <your-repo-url>"
echo "  git push -u origin main"
