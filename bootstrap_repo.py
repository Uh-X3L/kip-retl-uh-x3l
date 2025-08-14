from helpers.github_app_tools import resolve_installation_id, installation_token_cached, ensure_branch, put_file, open_pr, create_issue

README = """# kip-retl-uh-x3l
Bootstrap by AI agents.
"""
CI_YML = """name: ci
on:
  pull_request:
    branches: [ "main" ]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install ruff pytest
      - run: ruff check .
      - run: pytest -q || true
"""

if __name__ == "__main__":
    inst_id = resolve_installation_id()
    tok = installation_token_cached(inst_id)
    ensure_branch(tok, base_branch="main", new_branch="ai/dev")
    put_file(tok, "README.md", README, message="chore: add README")
    put_file(tok, ".github/workflows/ci.yml", CI_YML, message="ci: add workflow")
    pr = open_pr(tok, title="Bootstrap: README + CI", body="Adds README and CI workflow.")
    issue = create_issue(tok, title="Plan initial backlog", body="Supervisor: break down MVP into issues.")
    print("PR:", pr["html_url"])
    print("Issue:", issue["html_url"])
