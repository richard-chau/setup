#!/bin/bash
set -e

# Setup variables
GITHUB_USER="richard-chau"
GITHUB_EMAIL="winterandchaiyun@gmail.com"
SSH_KEY_PATH="$HOME/.ssh/id_ed25519"

echo "=== GitHub Auto-Setup with 'gh' ==="

# 0. Install gh CLI if not present
echo "--> Checking for GitHub CLI..."
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI not found. Installing..."
    sudo apt update
    sudo apt install gh -y
    echo "GitHub CLI installed successfully."
else
    echo "GitHub CLI is already installed."
fi

# 1. Git Configuration (Just to be safe/local)
echo "--> Configuring Git..."
git config --global user.name "$GITHUB_USER"
git config --global user.email "$GITHUB_EMAIL"

# 2. GitHub Authentication
echo "--> Checking GitHub Authentication..."
if ! gh auth status &>/dev/null; then
    echo "You are not logged in to GitHub CLI."
    echo "Please paste your GitHub Personal Access Token (Classic) below."
    echo "  (Scopes required: 'repo', 'read:org', 'admin:public_key')"
    echo "  Generate here: https://github.com/settings/tokens/new"
    read -r -s -p "Token: " GH_TOKEN
    echo ""
    
    if [ -z "$GH_TOKEN" ]; then
        echo "Error: Token cannot be empty."
        exit 1
    fi

    echo "$GH_TOKEN" | gh auth login --with-token
    echo "Logged in via token."
    
    # Configure gh to use SSH for git operations
    gh config set git_protocol ssh
else
    echo "Already logged in."
fi

# 3. SSH Setup
echo "--> Setting up SSH..."
if [ ! -f "$SSH_KEY_PATH" ]; then
    echo "Generating new SSH key..."
    ssh-keygen -t ed25519 -C "$GITHUB_EMAIL" -f "$SSH_KEY_PATH" -N ""
    eval "$(ssh-agent -s)"
    ssh-add "$SSH_KEY_PATH"
else
    echo "SSH key exists."
fi

# Upload SSH key to GitHub if not already there
# We use a unique title to avoid duplicates or errors if possible, 
# or just try to add and ignore "already exists" errors.
TITLE="Generated-$(date +%Y%m%d-%H%M)"
if gh ssh-key list | grep -q "$GITHUB_EMAIL"; then
    echo "An SSH key for this email is already on GitHub."
else
    echo "Uploading SSH key to GitHub..."
    gh ssh-key add "$SSH_KEY_PATH.pub" --title "$TITLE" || echo "Note: Key might already exist."
fi

# 4. Initialize and Commit
echo "--> Initializing Local Repository..."
if [ ! -d ".git" ]; then
    git init
    # Ensure there is something to commit
    if [ -z "$(ls -A)" ]; then
        echo "# Setup Project" > README.md
    fi
else
    echo "Git repo already active."
fi

echo "--> Committing files..."
git add .
if ! git diff-index --quiet HEAD --; then
    git commit -m "Initial setup commit"
else
    echo "Nothing to change."
fi

# 5. Create Remote Repo and Push
echo "--> Creating Remote Repository on GitHub..."
REPO_NAME=$(basename "$PWD")

# Check if repo exists
if gh repo view "$REPO_NAME" &>/dev/null; then
    echo "Repository '$REPO_NAME' already exists."
else
    # Create public repo, set remote to origin, and push
    # We use --ssh flag to ensure the remote URL uses git@github.com format
    gh repo create "$REPO_NAME" --public --source=. --remote=origin --push
    echo "Repository '$REPO_NAME' created and code pushed!"
fi

echo "=== Done! ==="
