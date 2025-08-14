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

def get_user_info(inst_token: str, username: str) -> Optional[Dict[str, Any]]:
    """
    Gets user information to verify if user exists and can be assigned.
    
    Args:
        inst_token (str): GitHub installation access token  
        username (str): GitHub username to check
        
    Returns:
        Optional[Dict[str, Any]]: User info if exists, None otherwise
    """
    try:
        url = f"https://api.github.com/users/{username}"
        r = requests.get(url, headers=_github_headers(inst_token), timeout=30)
        if r.status_code == 200:
            return r.json()
        return None
    except Exception:
        return None

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

def resolve_installation_id() -> int:
    """
    Resolves the installation ID from environment variable or by querying GitHub API.
    
    Returns:
        int: The GitHub App installation ID.
    """
    return int(INSTALLATION_ID_ENV) if INSTALLATION_ID_ENV.isdigit() else get_installation_id_for_repo()
