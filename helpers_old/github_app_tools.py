import os, time, base64, requests, json
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import jwt

load_dotenv()

APP_ID = int(os.environ["GITHUB_APP_ID"])
PRIVATE_KEY_PATH = os.environ["GITHUB_APP_PRIVATE_KEY_PEM"]
REPO = os.environ["GITHUB_REPO"]
INSTALLATION_ID_ENV = os.environ.get("GITHUB_INSTALLATION_ID", "").strip()
USER_AGENT = "ai-foundry-agent/1.0"

# Load the private key
with open(PRIVATE_KEY_PATH, 'r') as f:
    PRIVATE_KEY = f.read()

def _app_jwt() -> str:
    """ 
    This function creates a JSON Web Token (JWT) for the GitHub App.
    The JWT is signed with the private key and includes the app ID and expiration time.
    It follow the algorithm RS256 as required by GitHub.
    now + 540 seconds expiration time is used to ensure the token is valid for a reasonable period.
    now - 60 seconds is used to account for clock skew and ensure the token is valid immediately upon creation.
    APP_ID is the GitHub App ID, which is used to identify the app.
    jwt.encode() is used to create the JWT token.
    
    returns:
        str: The JWT token as a string.
        
    """
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 540, "iss": APP_ID}  # 9 min exp
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")     # RS256 required

def _github_headers(tok: str) -> Dict[str,str]:
    """
    Creates headers required for GitHub API requests.
    
    Args:
        tok (str): The token (app JWT or installation token) for authorization
        
    Returns:
        Dict[str, str]: Headers dictionary with Authorization, Accept, and User-Agent
    """
    return {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}

def get_installation_id_for_repo() -> int:
    """ Used this to populate the ENV variable GITHUB_INSTALLATION_ID """
    #TODO: Automatic population of all env variables?? is that possible with a correct az Login?
    owner, repo = REPO.split("/")
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/installation",
                     headers=_github_headers(_app_jwt()), timeout=30)
    r.raise_for_status()
    return int(r.json()["id"])

def get_installation_token(installation_id: int) -> str:
    """    Retrieves an installation access token for the GitHub App.
    Args:
        installation_id (int): The ID of the GitHub App installation.
    Returns:
        str: The installation access token.
    """
    r = requests.post(f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                      headers=_github_headers(_app_jwt()), timeout=30)
    r.raise_for_status()
    return r.json()["token"]  # ~1h token

_token_cache: Dict[str, Any] = {"token": None, "exp": 0.0}

def installation_token_cached(installation_id: int) -> str:
    """
    Retrieves a cached installation token or fetches a new one if expired.
    Uses 2-minute early refresh to avoid token expiration during operations.
    
    Args:
        installation_id (int): The ID of the GitHub App installation.
        
    Returns:
        str: The installation access token (valid for ~1 hour).
    """
    now = time.time()
    if _token_cache["token"] and now < _token_cache["exp"] - 120:  # refresh 2 min early
        return _token_cache["token"]
    
    tok = get_installation_token(installation_id)
    _token_cache["token"] = tok
    _token_cache["exp"] = now + 3600  # 1 hour from now
    return tok

def ensure_branch(inst_token: str, base_branch: str = "main", new_branch: str = "ai/dev") -> Dict[str, Any]:
    """
    Ensures a branch exists in the repository. Creates it from base_branch if it doesn't exist.
    
    Args:
        inst_token (str): GitHub installation access token
        base_branch (str, optional): Source branch to create from. Defaults to "main".
        new_branch (str, optional): Target branch name to ensure exists. Defaults to "ai/dev".
        
    Returns:
        Dict[str, Any]: Status information with 'status' key ('exists' or 'created')
        
    Raises:
        requests.HTTPError: If API requests fail
    """
    owner, repo = REPO.split("/")
    
    # Check if branch exists
    branch_url = f"https://api.github.com/repos/{owner}/{repo}/branches/{new_branch}"
    r = requests.get(branch_url, headers=_github_headers(inst_token), timeout=30)
    
    if r.status_code == 200:
        return {"status": "exists", "branch": new_branch}
    elif r.status_code != 404:
        # Unexpected error - not just "branch doesn't exist"
        print(f"[BRANCH WARN] Unexpected status {r.status_code} checking branch {new_branch}")
        r.raise_for_status()
    
    # Branch doesn't exist, create it from base_branch
    try:
        # First get the base branch SHA
        base_url = f"https://api.github.com/repos/{owner}/{repo}/branches/{base_branch}"
        base_r = requests.get(base_url, headers=_github_headers(inst_token), timeout=30)
        base_r.raise_for_status()
        base_sha = base_r.json()["commit"]["sha"]
        
        # Create new branch
        create_url = f"https://api.github.com/repos/{owner}/{repo}/git/refs"
        create_payload = {
            "ref": f"refs/heads/{new_branch}",
            "sha": base_sha
        }
        create_r = requests.post(create_url, headers=_github_headers(inst_token), json=create_payload, timeout=30)
        create_r.raise_for_status()
        
        return {"status": "created", "branch": new_branch, "from": base_branch}
        
    except requests.HTTPError as e:
        print(f"[BRANCH ERR] Failed to create branch {new_branch} from {base_branch}: {e}")
        raise

def put_file(inst_token: str, path: str, content_text: str, branch="ai/dev",
             message="AI bootstrap") -> Dict[str, Any]:
    """
    Creates or updates a file in the repository on the specified branch.
    Automatically handles SHA requirements for file updates and ensures branch exists.
    
    Args:
        inst_token (str): GitHub installation access token
        path (str): File path in the repository (e.g., "docs/readme.md")
        content_text (str): Content to write to the file
        branch (str, optional): Target branch name. Defaults to "ai/dev".
        message (str, optional): Commit message. Defaults to "AI bootstrap".
        
    Returns:
        Dict[str, Any]: GitHub API response with commit information
        
    Raises:
        requests.HTTPError: If file creation/update fails
    """
    owner, repo = REPO.split("/")
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    # Ensure branch exists first
    ensure_branch(inst_token, "main", branch)

    # Look up SHA on the target branch so updates succeed
    get = requests.get(url, headers=_github_headers(inst_token), params={"ref": branch}, timeout=30)
    
    payload = {
        "message": message,
        "content": base64.b64encode(content_text.encode("utf-8")).decode("ascii"),
        "branch": branch
    }
    
    # Only include SHA if file exists on the branch
    if get.status_code == 200:
        file_data = get.json()
        if isinstance(file_data, dict) and "sha" in file_data:
            payload["sha"] = file_data["sha"]
        elif isinstance(file_data, list) and len(file_data) > 0 and "sha" in file_data[0]:
            # Handle case where API returns array
            payload["sha"] = file_data[0]["sha"]

    r = requests.put(url, headers=_github_headers(inst_token), json=payload, timeout=30)
    
    if r.status_code >= 400:
        print(f"[PUT ERR] {r.status_code} for {path}")
        print("Request payload:", json.dumps(payload, indent=2))
        print("Response:", r.text)
    
    r.raise_for_status()
    return r.json()

def open_pr(inst_token: str, title: str, head="ai/dev", base="main", body="") -> Dict[str, Any]:
    """
    Opens a pull request from head branch to base branch.
    Handles existing PR errors gracefully by returning existing PR information.
    
    Args:
        inst_token (str): GitHub installation access token
        title (str): Pull request title
        head (str, optional): Source branch name. Defaults to "ai/dev".
        base (str, optional): Target branch name. Defaults to "main".
        body (str, optional): Pull request description. Defaults to "".
        
    Returns:
        Dict[str, Any]: GitHub API response with PR information, or existing PR info if duplicate
        
    Raises:
        requests.HTTPError: If PR creation fails (except for existing PR case)
    """
    owner, repo = REPO.split("/")
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    payload = {"title": title, "head": head, "base": base, "body": body}
    
    r = requests.post(url, headers=_github_headers(inst_token), json=payload, timeout=30)
    
    if r.status_code == 422:
        print("[PR ERR] 422 - Invalid request payload or no diff")
        print("Request JSON:", payload)
        print("Response:", r.text)
        try:
            error_details = r.json()
            if "message" in error_details:
                print("GitHub Error Message:", error_details["message"])
            if "errors" in error_details:
                print("GitHub Error Details:", error_details["errors"])
                # Check for existing PR error
                for error in error_details["errors"]:
                    if "pull request already exists" in error.get("message", "").lower():
                        # Return existing PR info instead of failing
                        print(f"[PR INFO] Fetching existing PR for {owner}:{head} -> {base}")
                        existing_prs = requests.get(
                            f"https://api.github.com/repos/{owner}/{repo}/pulls",
                            headers=_github_headers(inst_token),
                            params={"head": f"{owner}:{head}", "base": base, "state": "open"},
                            timeout=30
                        )
                        if existing_prs.status_code == 200 and existing_prs.json():
                            existing_pr = existing_prs.json()[0]
                            print(f"[PR INFO] Found existing PR: {existing_pr.get('html_url', 'N/A')}")
                            return {"status": "exists", "pr": existing_pr, "html_url": existing_pr.get("html_url")}
                        else:
                            print("[PR WARN] Could not fetch existing PR details")
                            return {"status": "error", "message": "PR already exists but couldn't fetch details"}
        except Exception as e:
            print(f"Could not parse error response as JSON: {e}")
        
        # If we couldn't handle the error gracefully, still raise it
        r.raise_for_status()
    
    r.raise_for_status()
    return r.json()

def create_issue(inst_token: str, title: str, body="", assignees=None, labels=None, milestone=None) -> Dict[str, Any]:
    """
    Creates a new issue in the repository with enhanced features.
    
    Args:
        inst_token (str): GitHub installation access token
        title (str): Issue title
        body (str, optional): Issue description. Defaults to "".
        assignees (list, optional): List of username strings to assign. Defaults to None.
        labels (list, optional): List of label names to apply. Defaults to None.
        milestone (int, optional): Milestone number to assign. Defaults to None.
        
    Returns:
        Dict[str, Any]: GitHub API response with issue information
        
    Raises:
        requests.HTTPError: If issue creation fails
    """
    owner, repo = REPO.split("/")
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    
    payload = {"title": title, "body": body}
    
    if assignees:
        payload["assignees"] = assignees if isinstance(assignees, list) else [assignees]
    if labels:
        payload["labels"] = labels if isinstance(labels, list) else [labels]
    if milestone:
        payload["milestone"] = milestone
    
    r = requests.post(url, headers=_github_headers(inst_token), json=payload, timeout=30)
    
    if r.status_code >= 400:
        print(f"[CREATE ISSUE ERR] {r.status_code} for issue creation")
        print("Request payload:", json.dumps(payload, indent=2))
        print("Response:", r.text)
        
    r.raise_for_status()
    return r.json()

def add_issue_to_project(inst_token: str, issue_id: int, project_id: int, column_name: str = "To Do") -> Dict[str, Any]:
    """
    Adds an issue to a GitHub project (classic projects).
    
    Args:
        inst_token (str): GitHub installation access token
        issue_id (int): GitHub issue ID
        project_id (int): GitHub project ID
        column_name (str, optional): Project column name. Defaults to "To Do".
        
    Returns:
        Dict[str, Any]: GitHub API response
        
    Raises:
        requests.HTTPError: If adding to project fails
    """
    owner, repo = REPO.split("/")
    
    # First, get project columns
    columns_url = f"https://api.github.com/projects/{project_id}/columns"
    columns_headers = _github_headers(inst_token)
    columns_headers["Accept"] = "application/vnd.github.inertia-preview+json"
    
    columns_r = requests.get(columns_url, headers=columns_headers, timeout=30)
    columns_r.raise_for_status()
    columns = columns_r.json()
    
    # Find the target column
    column_id = None
    for column in columns:
        if column["name"].lower() == column_name.lower():
            column_id = column["id"]
            break
    
    if not column_id and columns:
        # Fallback to first column if target not found
        column_id = columns[0]["id"]
        print(f"[PROJECT WARN] Column '{column_name}' not found, using '{columns[0]['name']}'")
    
    if not column_id:
        raise ValueError(f"No columns found in project {project_id}")
    
    # Add issue to column
    cards_url = f"https://api.github.com/projects/columns/{column_id}/cards"
    card_payload = {
        "content_id": issue_id,
        "content_type": "Issue"
    }
    
    cards_r = requests.post(cards_url, headers=columns_headers, json=card_payload, timeout=30)
    cards_r.raise_for_status()
    return cards_r.json()

def create_labels_if_not_exist(inst_token: str, labels: List[Dict[str, str]]) -> List[str]:
    """
    Creates repository labels if they don't exist.
    
    Args:
        inst_token (str): GitHub installation access token
        labels (List[Dict[str, str]]): List of label definitions with 'name', 'color', and 'description'
        
    Returns:
        List[str]: List of label names that were created or already existed
        
    Raises:
        requests.HTTPError: If label creation fails unexpectedly
    """
    owner, repo = REPO.split("/")
    created_labels = []
    
    for label in labels:
        label_name = label["name"]
        # GitHub labels have a 50 character limit
        if len(label_name) > 50:
            print(f"⚠️ Label name too long (>{len(label_name)} chars), truncating: {label_name}")
            label_name = label_name[:47] + "..."
            
        url = f"https://api.github.com/repos/{owner}/{repo}/labels"
        
        # Check if label exists
        check_r = requests.get(f"{url}/{label_name}", headers=_github_headers(inst_token), timeout=30)
        
        if check_r.status_code == 200:
            created_labels.append(label_name)
            continue
        elif check_r.status_code != 404:
            check_r.raise_for_status()
        
        # Create label if it doesn't exist
        create_payload = {
            "name": label["name"],
            "color": label.get("color", "007fff"),
            "description": label.get("description", "")
        }
        
        create_r = requests.post(url, headers=_github_headers(inst_token), json=create_payload, timeout=30)
        if create_r.status_code == 201:
            created_labels.append(label_name)
        elif create_r.status_code != 422:  # 422 might mean label already exists
            create_r.raise_for_status()
        else:
            print(f"[LABEL WARN] Could not create label '{label_name}': {create_r.text}")
            
    return created_labels



def link_issues(inst_token: str, parent_issue_id: int, child_issue_ids: List[int], relation_type: str = "subtask") -> None:
    """
    Links issues together by adding references in comments (GitHub doesn't have native sub-issues).
    
    Args:
        inst_token (str): GitHub installation access token
        parent_issue_id (int): Parent issue number
        child_issue_ids (List[int]): List of child issue numbers
        relation_type (str, optional): Type of relation. Defaults to "subtask".
    """
    owner, repo = REPO.split("/")
    
    # Add comment to parent issue listing all subtasks
    parent_comment = f"## 🔗 {relation_type.title()} Issues\n\n"
    parent_comment += f"This issue has been broken down into the following {relation_type}s:\n\n"
    
    for child_id in child_issue_ids:
        parent_comment += f"- #{child_id}\n"
    
    parent_comment += f"\n---\n*Auto-generated by Backend Supervisor Agent*"
    
    parent_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{parent_issue_id}/comments"
    requests.post(parent_url, headers=_github_headers(inst_token), 
                 json={"body": parent_comment}, timeout=30)
    
    # Add comment to each child issue referencing the parent
    for child_id in child_issue_ids:
        child_comment = f"## 🔗 Parent Issue\n\nThis is a {relation_type} of #{parent_issue_id}\n\n"
        child_comment += f"---\n*Auto-generated by Backend Supervisor Agent*"
        
        child_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{child_id}/comments"
        requests.post(child_url, headers=_github_headers(inst_token),
                     json={"body": child_comment}, timeout=30)

def get_user_info(inst_token: str, username: str) -> Optional[Dict[str, Any]]:
    """
    Get GitHub user information to verify if user exists and can be assigned.
    
    Args:
        inst_token (str): GitHub installation access token
        username (str): GitHub username to look up
        
    Returns:
        Optional[Dict[str, Any]]: User info dict or None if not found
    """
    try:
        url = f"https://api.github.com/users/{username}"
        r = requests.get(url, headers=_github_headers(inst_token), timeout=30)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception as e:
        print(f"❌ Error getting user info for {username}: {e}")
        return None

def resolve_installation_id() -> int:
    """
    Resolves the installation ID from environment variable or by querying GitHub API.
    
    Returns:
        int: The GitHub App installation ID.
    """
    return int(INSTALLATION_ID_ENV) if INSTALLATION_ID_ENV.isdigit() else get_installation_id_for_repo()


def create_project_issue_with_subtasks(
    title: str,
    description: str,
    subtasks: List[Dict[str, Any]],
    project_metadata: Optional[Dict[str, Any]] = None,
    creator_name: str = "AI Agent",
    assignee: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a comprehensive GitHub issue with subtasks, labels, and project management features.
    
    Args:
        title (str): Main issue title
        description (str): Main issue description/body
        subtasks (List[Dict]): List of subtask dictionaries with keys: title, description, estimated_hours, agent_type, skills_required, dependencies
        project_metadata (Optional[Dict]): Additional project metadata (complexity, technologies, etc.)
        creator_name (str): Name of the creating agent/system
        assignee (Optional[str]): GitHub username to assign the main issue to
        
    Returns:
        Dict[str, Any]: Enhanced result with main issue, sub-issues, and metadata
    """
    inst_id = resolve_installation_id()
    tok = installation_token_cached(inst_id)
    
    total_hours = sum(float(task.get("estimated_hours", 0)) for task in subtasks)
    total_tasks = len(subtasks)
    
    # Extract metadata
    metadata = project_metadata or {}
    complexity_raw = metadata.get("complexity", "medium")
    # Ensure complexity is just the basic level (truncate long descriptions)
    if isinstance(complexity_raw, str):
        complexity_words = complexity_raw.lower().split()
        if any(word in complexity_words for word in ["low", "simple", "easy"]):
            complexity = "low"
        elif any(word in complexity_words for word in ["high", "complex", "difficult", "expert"]):
            complexity = "high"
        else:
            complexity = "medium"  # Default for anything with "medium" or unrecognized
    else:
        complexity = "medium"
    
    technologies = metadata.get("technologies", [])
    agent_types = set(task.get("agent_type", "general") for task in subtasks)

    # 🏷️ Create project-specific labels
    creator_label = creator_name.lower().replace(" ", "-")
    if len(creator_label) > 45:  # Leave room for other characters
        creator_label = creator_label[:42] + "..."
        
    project_labels = [
        {"name": creator_label, "color": "7f00ff", "description": f"Created by {creator_name}"},
        {"name": f"complexity-{complexity}", "color": _get_complexity_color(complexity), "description": f"Project complexity: {complexity}"},
        {"name": "ai-project", "color": "00d4aa", "description": "AI-managed project"},
        {"name": "has-subtasks", "color": "ffa500", "description": "Parent issue with sub-issues"}
    ]
    
    # Add agent-type specific labels
    for agent_type in agent_types:
        project_labels.append({
            "name": f"needs-{agent_type}",
            "color": _get_agent_color(agent_type),
            "description": f"Requires {agent_type} agent"
        })
    
    print("🏷️ Creating project labels...")
    created_labels = create_labels_if_not_exist(tok, project_labels)
    
    # Validate assignee
    assignees = None
    if assignee:
        user_info = get_user_info(tok, assignee)
        if user_info:
            assignees = [assignee]
            print(f"✅ Will assign issue to: {assignee}")
        else:
            print(f"⚠️ User '{assignee}' not found, creating issue without assignee")
    
    # Create main issue
    print("📝 Creating main project issue...")
    result = create_issue(
        tok,
        title=title,
        body=description,
        assignees=assignees,
        labels=[label["name"] for label in project_labels if label["name"] in created_labels]
    )
    
    main_issue_number = result["number"]
    print(f"✅ Created main issue #{main_issue_number}: {result.get('html_url')}")
    
    # 🎯 Create sub-issues for each subtask
    print(f"🔄 Creating {len(subtasks)} sub-issues...")
    sub_issue_numbers = []
    sub_issue_details = []
    
    for i, task in enumerate(subtasks, 1):
        agent_type = task.get("agent_type", "general")
        sub_issue_title = f"{_get_agent_emoji(agent_type)} {task['title']}"
        
        sub_issue_body = f"""## 🎯 Subtask Details

**Parent Issue:** #{main_issue_number}
**Agent Type:** {agent_type.title()}
**Estimated Hours:** {task.get('estimated_hours', 0)}h
**Skills Required:** {', '.join(task.get('skills_required', []))}

### 📝 Description
{task['description']}

### ✅ Acceptance Criteria
- [ ] Task implementation completed
- [ ] Code follows project standards
- [ ] Tests passing (if applicable)
- [ ] Documentation updated (if applicable)
- [ ] Peer review completed
- [ ] Integration with main project verified

### 🔗 Dependencies
{chr(10).join([f"- {dep}" for dep in task.get('dependencies', [])]) if task.get('dependencies') else "None"}

### 📊 Task Metadata
- **Complexity:** Individual task within {complexity.title()} project
- **Technology Stack:** {', '.join(technologies[:3])}{'...' if len(technologies) > 3 else ''}
- **Priority:** {_determine_task_priority(task, i, len(subtasks))}

---
*Sub-issue created by {creator_name}*
"""
        
        # Create sub-issue with appropriate labels
        creator_label = creator_name.lower().replace(" ", "-")
        if len(creator_label) > 45:  # Leave room for other characters
            creator_label = creator_label[:42] + "..."
            
        sub_labels = [
            creator_label,
            f"agent-{agent_type}",
            "subtask",
            f"complexity-{complexity}"
        ]
        
        sub_result = create_issue(
            tok,
            title=sub_issue_title,
            body=sub_issue_body,
            labels=sub_labels
        )
        
        sub_issue_numbers.append(sub_result["number"])
        sub_issue_details.append({
            "number": sub_result["number"],
            "title": task["title"],
            "html_url": sub_result.get("html_url"),
            "labels": sub_labels,
            "agent_type": agent_type
        })
        print(f"  ✅ Created sub-issue #{sub_result['number']}: {task['title']}")
    
    # 🔗 Link all sub-issues to the main issue
    print("🔗 Linking sub-issues to main issue...")
    link_issues(tok, main_issue_number, sub_issue_numbers, "subtask")
    
    # 📋 Try to add to project (optional)
    project_id = os.environ.get("GITHUB_PROJECT_ID")
    if project_id:
        try:
            print(f"📋 Adding main issue to project #{project_id}...")
            add_issue_to_project(tok, main_issue_number, int(project_id), "To Do")
            print("✅ Added main issue to project")
        except Exception as e:
            print(f"⚠️ Could not add to project: {e}")
    
    # Return enhanced result with sub-issue information
    return {
        **result,
        "sub_issues": sub_issue_details,
        "total_issues_created": len(sub_issue_numbers) + 1,
        "labels_created": created_labels,
        "main_issue_number": main_issue_number,
        "sub_issue_numbers": sub_issue_numbers,
        "total_estimated_hours": total_hours,
        "agent_types": list(agent_types)
    }


def _get_complexity_color(complexity: str) -> str:
    """Get color code for complexity label."""
    colors = {
        "low": "28a745",
        "medium": "ffc107", 
        "high": "fd7e14",
        "expert": "dc3545"
    }
    return colors.get(complexity.lower(), "6c757d")


def _get_agent_color(agent_type: str) -> str:
    """Get color code for agent type label."""
    colors = {
        "worker": "0366d6",
        "testing": "28a745",
        "documentation": "6f42c1",
        "research": "e36209",
        "devops": "d73a49",
        "general": "6c757d"
    }
    return colors.get(agent_type, "6c757d")


def _get_agent_emoji(agent_type: str) -> str:
    """Get emoji for agent type."""
    emojis = {
        "worker": "🔨",
        "testing": "🧪",
        "documentation": "📚", 
        "research": "🔍",
        "devops": "🚀",
        "general": "⚙️"
    }
    return emojis.get(agent_type, "⚙️")


def _determine_task_priority(task: Dict[str, Any], position: int, total: int) -> str:
    """Determine task priority based on position and dependencies."""
    if task.get("dependencies"):
        return "High"  # Tasks with dependencies are high priority
    elif position <= total * 0.3:
        return "High"  # First 30% of tasks
    elif position <= total * 0.7:
        return "Medium" # Middle 40% of tasks
    else:
        return "Low"   # Last 30% of tasks


def cleanup_all_issues(inst_token: str, confirm_deletion: bool = False, dry_run: bool = True) -> Dict[str, Any]:
    """
    Cleanup utility to close or delete all issues in the repository.
    ⚠️ WARNING: This will close ALL issues in the repository!
    
    Args:
        inst_token (str): GitHub installation access token
        confirm_deletion (bool): Must be True to actually perform cleanup
        dry_run (bool): If True, only lists issues without closing them
        
    Returns:
        Dict[str, Any]: Summary of cleanup operation
        
    Raises:
        ValueError: If confirmation not provided for non-dry-run
        requests.HTTPError: If GitHub API requests fail
    """
    owner, repo = REPO.split("/")
    
    if not dry_run and not confirm_deletion:
        raise ValueError("Must set confirm_deletion=True to actually close issues (safety check)")
    
    print(f"🧹 {'DRY RUN: ' if dry_run else ''}Cleanup operation for {owner}/{repo}")
    print("=" * 60)
    
    # Get all open issues
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {
        "state": "open",
        "per_page": 100,  # GitHub max per page
        "sort": "created",
        "direction": "desc"
    }
    
    all_issues = []
    page = 1
    
    while True:
        params["page"] = page
        r = requests.get(url, headers=_github_headers(inst_token), params=params, timeout=30)
        r.raise_for_status()
        
        issues = r.json()
        if not issues:
            break
            
        # Filter out pull requests (they appear in issues API)
        real_issues = [issue for issue in issues if not issue.get("pull_request")]
        all_issues.extend(real_issues)
        
        if len(issues) < 100:  # Last page
            break
        page += 1
    
    print(f"📊 Found {len(all_issues)} open issues to process")
    
    if not all_issues:
        return {"status": "no_issues", "message": "No issues found to cleanup"}
    
    if dry_run:
        print("\n🔍 Issues that would be closed:")
        for issue in all_issues:
            labels = [label["name"] for label in issue.get("labels", [])]
            print(f"  • #{issue['number']}: {issue['title'][:70]}...")
            if labels:
                print(f"    🏷️ Labels: {', '.join(labels[:5])}{'...' if len(labels) > 5 else ''}")
        
        return {
            "status": "dry_run",
            "issues_found": len(all_issues),
            "message": f"Dry run complete. {len(all_issues)} issues would be closed."
        }
    
    # Actually close the issues
    print(f"\n🗑️ Closing {len(all_issues)} issues...")
    closed_count = 0
    failed_count = 0
    
    for issue in all_issues:
        try:
            issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue['number']}"
            close_payload = {
                "state": "closed",
                "state_reason": "completed"  # or "not_planned"
            }
            
            close_r = requests.patch(issue_url, headers=_github_headers(inst_token), 
                                   json=close_payload, timeout=30)
            close_r.raise_for_status()
            
            closed_count += 1
            print(f"  ✅ Closed #{issue['number']}: {issue['title'][:50]}...")
            
        except requests.HTTPError as e:
            failed_count += 1
            print(f"  ❌ Failed to close #{issue['number']}: {e}")
        except Exception as e:
            failed_count += 1
            print(f"  ❌ Error closing #{issue['number']}: {e}")
    
    print(f"\n📋 Cleanup Summary:")
    print(f"   ✅ Successfully closed: {closed_count}")
    print(f"   ❌ Failed to close: {failed_count}")
    print(f"   📊 Total processed: {len(all_issues)}")
    
    return {
        "status": "completed",
        "issues_processed": len(all_issues),
        "issues_closed": closed_count,
        "issues_failed": failed_count,
        "success_rate": f"{(closed_count/len(all_issues)*100):.1f}%" if all_issues else "0%"
    }


def cleanup_test_issues_only(inst_token: str, confirm_deletion: bool = False, dry_run: bool = True) -> Dict[str, Any]:
    """
    Cleanup utility to close only test-related issues (safer than cleanup_all_issues).
    Identifies test issues by common patterns in titles and labels.
    
    Args:
        inst_token (str): GitHub installation access token
        confirm_deletion (bool): Must be True to actually perform cleanup
        dry_run (bool): If True, only lists issues without closing them
        
    Returns:
        Dict[str, Any]: Summary of cleanup operation
    """
    owner, repo = REPO.split("/")
    
    if not dry_run and not confirm_deletion:
        raise ValueError("Must set confirm_deletion=True to actually close issues (safety check)")
    
    print(f"🧪 {'DRY RUN: ' if dry_run else ''}Test Issues Cleanup for {owner}/{repo}")
    print("=" * 60)
    
    # Get all open issues
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {"state": "open", "per_page": 100}
    
    r = requests.get(url, headers=_github_headers(inst_token), params=params, timeout=30)
    r.raise_for_status()
    issues = r.json()
    
    # Filter for test-related issues
    test_patterns = [
        "test", "debug", "simple", "hello world", "generic function",
        "backend supervisor", "api endpoint", "health check", "minimal",
        "🧪", "🔧", "🎯", "emoji test"
    ]
    
    test_label_patterns = [
        "test-agent", "complexity-", "ai-project", "has-subtasks",
        "needs-worker", "needs-testing", "subtask"
    ]
    
    test_issues = []
    for issue in issues:
        if issue.get("pull_request"):  # Skip PRs
            continue
            
        title = issue["title"].lower()
        labels = [label["name"].lower() for label in issue.get("labels", [])]
        
        # Check if issue matches test patterns
        is_test_issue = any(pattern.lower() in title for pattern in test_patterns)
        has_test_labels = any(any(pattern in label for pattern in test_label_patterns) for label in labels)
        
        if is_test_issue or has_test_labels:
            test_issues.append(issue)
    
    print(f"📊 Found {len(test_issues)} test-related issues out of {len(issues)} total")
    
    if not test_issues:
        return {"status": "no_test_issues", "message": "No test issues found to cleanup"}
    
    if dry_run:
        print("\n🔍 Test issues that would be closed:")
        for issue in test_issues:
            labels = [label["name"] for label in issue.get("labels", [])]
            print(f"  • #{issue['number']}: {issue['title']}")
            if labels:
                print(f"    🏷️ Labels: {', '.join(labels[:3])}{'...' if len(labels) > 3 else ''}")
        
        return {
            "status": "dry_run",
            "test_issues_found": len(test_issues),
            "total_issues": len(issues),
            "message": f"Dry run complete. {len(test_issues)} test issues would be closed."
        }
    
    # Close the test issues
    print(f"\n🗑️ Closing {len(test_issues)} test issues...")
    closed_count = 0
    
    for issue in test_issues:
        try:
            issue_url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue['number']}"
            close_r = requests.patch(issue_url, headers=_github_headers(inst_token),
                                   json={"state": "closed", "state_reason": "completed"}, timeout=30)
            close_r.raise_for_status()
            
            closed_count += 1
            print(f"  ✅ Closed #{issue['number']}: {issue['title'][:60]}...")
            
        except Exception as e:
            print(f"  ❌ Failed to close #{issue['number']}: {e}")
    
    return {
        "status": "completed",
        "test_issues_closed": closed_count,
        "total_test_issues": len(test_issues),
        "success_rate": f"{(closed_count/len(test_issues)*100):.1f}%" if test_issues else "0%"
    }
