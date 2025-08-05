#!/bin/bash

# Montu Manager Ecosystem - Branch Management Script
# This script helps manage the multi-application branching strategy

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Application prefixes
declare -A APP_PREFIXES=(
    ["project-launcher"]="pl"
    ["task-creator"]="tc"
    ["dcc-integration"]="dcc"
    ["review-app"]="ra"
    ["shared"]="shared"
    ["infra"]="infra"
)

# Function to display usage
usage() {
    echo -e "${BLUE}Montu Manager Branch Management Script${NC}"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  create-feature    Create a new feature branch"
    echo "  list-branches     List all branches by category"
    echo "  status           Show current branch status"
    echo "  switch-phase     Switch to a different phase integration branch"
    echo "  cleanup          Clean up merged feature branches"
    echo ""
    echo "Examples:"
    echo "  $0 create-feature project-launcher project-selection-ui 1"
    echo "  $0 list-branches"
    echo "  $0 status"
    echo "  $0 switch-phase 2"
    echo ""
}

# Function to create a feature branch
create_feature_branch() {
    local app_name=$1
    local feature_name=$2
    local phase=$3
    
    if [[ -z "$app_name" || -z "$feature_name" || -z "$phase" ]]; then
        echo -e "${RED}Error: Missing required parameters${NC}"
        echo "Usage: $0 create-feature <app-name> <feature-name> <phase>"
        echo "Available apps: ${!APP_PREFIXES[@]}"
        exit 1
    fi
    
    # Get app prefix
    local app_prefix=${APP_PREFIXES[$app_name]}
    if [[ -z "$app_prefix" ]]; then
        echo -e "${RED}Error: Unknown application '$app_name'${NC}"
        echo "Available apps: ${!APP_PREFIXES[@]}"
        exit 1
    fi
    
    # Create branch name
    local branch_name="feature/${app_prefix}/${feature_name}"
    local base_branch="integration/phase-${phase}"
    
    echo -e "${BLUE}Creating feature branch: ${branch_name}${NC}"
    echo -e "${YELLOW}Base branch: ${base_branch}${NC}"
    
    # Check if base branch exists
    if ! git show-ref --verify --quiet refs/heads/${base_branch}; then
        echo -e "${RED}Error: Base branch '${base_branch}' does not exist${NC}"
        exit 1
    fi
    
    # Switch to base branch and pull latest
    git checkout ${base_branch}
    git pull origin ${base_branch}
    
    # Create and switch to feature branch
    git checkout -b ${branch_name}
    
    echo -e "${GREEN}Successfully created and switched to branch: ${branch_name}${NC}"
    echo -e "${YELLOW}Remember to push the branch when ready: git push -u origin ${branch_name}${NC}"
}

# Function to list branches by category
list_branches() {
    echo -e "${BLUE}=== Montu Manager Branch Structure ===${NC}"
    echo ""
    
    echo -e "${GREEN}Main Branches:${NC}"
    git branch -a | grep -E "(main|develop)" | sed 's/^/  /'
    echo ""
    
    echo -e "${GREEN}Phase Integration Branches:${NC}"
    git branch -a | grep "integration/phase" | sed 's/^/  /' || echo "  No phase branches found"
    echo ""
    
    echo -e "${GREEN}Application Integration Branches:${NC}"
    git branch -a | grep "app/" | sed 's/^/  /' || echo "  No app integration branches found"
    echo ""
    
    echo -e "${GREEN}Feature Branches by Application:${NC}"
    for app in "${!APP_PREFIXES[@]}"; do
        local prefix=${APP_PREFIXES[$app]}
        local branches=$(git branch -a | grep "feature/${prefix}/" || true)
        if [[ -n "$branches" ]]; then
            echo -e "  ${YELLOW}${app} (${prefix}):${NC}"
            echo "$branches" | sed 's/^/    /'
        fi
    done
    echo ""
    
    echo -e "${GREEN}Release Branches:${NC}"
    git branch -a | grep "release/" | sed 's/^/  /' || echo "  No release branches found"
    echo ""
    
    echo -e "${GREEN}Hotfix Branches:${NC}"
    git branch -a | grep "hotfix/" | sed 's/^/  /' || echo "  No hotfix branches found"
}

# Function to show current status
show_status() {
    echo -e "${BLUE}=== Current Branch Status ===${NC}"
    echo ""
    
    local current_branch=$(git branch --show-current)
    echo -e "${GREEN}Current Branch:${NC} ${current_branch}"
    
    # Determine branch type and context
    if [[ "$current_branch" == "main" ]]; then
        echo -e "${YELLOW}Context:${NC} Production branch"
    elif [[ "$current_branch" == "develop" ]]; then
        echo -e "${YELLOW}Context:${NC} Main development integration branch"
    elif [[ "$current_branch" =~ ^integration/phase-([0-9]+)$ ]]; then
        local phase=${BASH_REMATCH[1]}
        echo -e "${YELLOW}Context:${NC} Phase ${phase} integration branch"
    elif [[ "$current_branch" =~ ^feature/([^/]+)/(.+)$ ]]; then
        local app_prefix=${BASH_REMATCH[1]}
        local feature_name=${BASH_REMATCH[2]}
        
        # Find app name from prefix
        local app_name=""
        for app in "${!APP_PREFIXES[@]}"; do
            if [[ "${APP_PREFIXES[$app]}" == "$app_prefix" ]]; then
                app_name=$app
                break
            fi
        done
        
        echo -e "${YELLOW}Context:${NC} Feature branch for ${app_name:-unknown} (${feature_name})"
    fi
    
    echo ""
    echo -e "${GREEN}Branch Status:${NC}"
    git status --porcelain | head -10
    
    if [[ $(git status --porcelain | wc -l) -gt 10 ]]; then
        echo "  ... and $(( $(git status --porcelain | wc -l) - 10 )) more files"
    fi
    
    echo ""
    echo -e "${GREEN}Recent Commits:${NC}"
    git log --oneline -5
}

# Function to switch to phase integration branch
switch_phase() {
    local phase=$1
    
    if [[ -z "$phase" ]]; then
        echo -e "${RED}Error: Phase number required${NC}"
        echo "Usage: $0 switch-phase <phase-number>"
        exit 1
    fi
    
    local branch_name="integration/phase-${phase}"
    
    echo -e "${BLUE}Switching to phase integration branch: ${branch_name}${NC}"
    
    # Check if branch exists locally
    if git show-ref --verify --quiet refs/heads/${branch_name}; then
        git checkout ${branch_name}
        git pull origin ${branch_name}
    else
        # Try to checkout from remote
        if git show-ref --verify --quiet refs/remotes/origin/${branch_name}; then
            git checkout -b ${branch_name} origin/${branch_name}
        else
            echo -e "${RED}Error: Branch '${branch_name}' does not exist locally or remotely${NC}"
            exit 1
        fi
    fi
    
    echo -e "${GREEN}Successfully switched to: ${branch_name}${NC}"
}

# Function to clean up merged branches
cleanup_branches() {
    echo -e "${BLUE}Cleaning up merged feature branches...${NC}"
    
    # Get list of merged branches (excluding main, develop, and integration branches)
    local merged_branches=$(git branch --merged | grep -E "feature/" | grep -v "\*" || true)
    
    if [[ -z "$merged_branches" ]]; then
        echo -e "${GREEN}No merged feature branches to clean up${NC}"
        return
    fi
    
    echo -e "${YELLOW}The following merged feature branches will be deleted:${NC}"
    echo "$merged_branches"
    echo ""
    
    read -p "Are you sure you want to delete these branches? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "$merged_branches" | xargs -n 1 git branch -d
        echo -e "${GREEN}Cleanup completed${NC}"
    else
        echo -e "${YELLOW}Cleanup cancelled${NC}"
    fi
}

# Main script logic
case "${1:-}" in
    "create-feature")
        create_feature_branch "$2" "$3" "$4"
        ;;
    "list-branches")
        list_branches
        ;;
    "status")
        show_status
        ;;
    "switch-phase")
        switch_phase "$2"
        ;;
    "cleanup")
        cleanup_branches
        ;;
    "help"|"-h"|"--help")
        usage
        ;;
    *)
        echo -e "${RED}Error: Unknown command '${1:-}'${NC}"
        echo ""
        usage
        exit 1
        ;;
esac
