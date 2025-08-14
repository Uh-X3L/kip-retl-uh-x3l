import os, time, base64, requests, json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
import jwt

load_dotenv()

APP_ID = int(os.environ["GITHUB_APP_ID"])
PRIVATE_KEY_PATH = os.environ["GITHUB_APP_PRIVATE_KEY_PEM"]
REPO = os.environ["GITHUB_REPO"]
INSTALLATION_ID_ENV = os.environ.get("GITHUB_INSTALLATION_ID", "").strip()
USER_AGENT = "ai-foundry-agent/1.0"

with open(PRIVATE_KEY_PATH, "r", encoding="utf-8") as f:
    PRIVATE_KEY = f.read()

def _app_jwt() -> str:
    now = int(time.time())
    payload = {"iat": now - 60, "exp": now + 540, "iss": APP_ID}  # 9 min exp
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")     # RS256 required

def _app_headers(tok: str) -> Dict[str,str]:
    return {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}

def _inst_headers(tok: str) -> Dict[str,str]:
    return {"Authorization": f"Bearer {tok}", "Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}

def get_installation_id_for_repo() -> int:
    owner, repo = REPO.split("/")
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/installation",
                     headers=_app_headers(_app_jwt()), timeout=30)
    r.raise_for_status()
    return int(r.json()["id"])  # numeric ID

def get_installation_token(installation_id: int) -> str:
    r = requests.post(f"https://api.github.com/app/installations/{installation_id}/access_tokens",
                      headers=_app_headers(_app_jwt()), timeout=30)
    r.raise_for_status()
    return r.json()["token"]  # ~1h token

_cache = {"token": None, "exp": 0.0}
def installation_token_cached(installation_id: int) -> str:
    now = time.time()
    if _cache["token"] and now < _cache["exp"] - 120:  # refresh 2 min early
        return _cache["token"]
    tok = get_installation_token(installation_id)
    _cache["token"] = tok
    _cache["exp"] = now + 3600
    return tok

def ensure_branch(inst_token: str, base_branch="main", new_branch="ai/dev"):
    # does new_branch exist?
    owner, repo = REPO.split("/")
    ref_url = f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{new_branch}"
    r = requests.get(ref_url, headers=_inst_headers(inst_token), timeout=30)
    if r.status_code == 200:
        return  # already exists
    # get base branch sha
    r = requests.get(f"https://api.github.com/repos/{owner}/{repo}/git/ref/heads/{base_branch}",
                     headers=_inst_headers(inst_token), timeout=30)
    r.raise_for_status()
    base_sha = r.json()["object"]["sha"]
    # create the branch ref
    r = requests.post(f"https://api.github.com/repos/{owner}/{repo}/git/refs",
                      headers=_inst_headers(inst_token),
                      json={"ref": f"refs/heads/{new_branch}", "sha": base_sha}, timeout=30)
    r.raise_for_status()

def put_file(inst_token: str, path: str, content_text: str, branch="ai/dev",
             message="AI bootstrap") -> Dict[str, Any]:
    owner, repo = REPO.split("/")
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    # Try to retrieve current SHA if file exists
    resp = requests.get(url, headers=_inst_headers(inst_token), timeout=30)
    sha = None
    if resp.status_code == 200:
        sha = resp.json().get("sha")

    payload = {
        "message": message,
        "content": base64.b64encode(content_text.encode("utf-8")).decode("ascii"),
        "branch": branch
    }
    if sha:
        payload["sha"] = sha  # Required when updating an existing file

    r = requests.put(url, headers=_inst_headers(inst_token), json=payload, timeout=30)
    if r.status_code >= 400:
        print("[PUT ERR]", r.status_code, r.text)
    r.raise_for_status()
    return r.json()

def open_pr(inst_token: str, title: str, head="ai/dev", base="main", body="") -> Dict[str, Any]:
    owner, repo = REPO.split("/")
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    payload = {"title": title, "head": head, "base": base, "body": body}
    r = requests.post(url, headers=_inst_headers(inst_token), json=payload, timeout=30)
    r.raise_for_status()
    return r.json()

def create_issue(inst_token: str, title: str, body="") -> Dict[str, Any]:
    owner, repo = REPO.split("/")
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    r = requests.post(url, headers=_inst_headers(inst_token), json={"title": title, "body": body}, timeout=30)
    r.raise_for_status()
    return r.json()

def resolve_installation_id() -> int:
    return int(INSTALLATION_ID_ENV) if INSTALLATION_ID_ENV.isdigit() else get_installation_id_for_repo()
