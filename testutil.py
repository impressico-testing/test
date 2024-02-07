import requests
import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def get_commits_count(owner, repo, username, token):
    base_url = "https://api.github.com"
    url = f"{base_url}/repos/{owner}/{repo}/commits"
    headers = {"Authorization": f"token {token}"}

    today = datetime.date.today()
    last_week = today - datetime.timedelta(days=7)

    params = {
        "author": username,
        "since": last_week.strftime("%Y-%m-%d"),
        "until": today.strftime("%Y-%m-%d")
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    commits = response.json()
    return len(commits)

def get_pull_requests_count(owner, repo, username, token):
    base_url = "https://api.github.com"
    url = f"{base_url}/repos/{owner}/{repo}/pulls"
    headers = {"Authorization": f"token {token}"}

    today = datetime.date.today()
    last_week = today - datetime.timedelta(days=7)

    params = {
        "author": username,
        "state": "all",
        "since": last_week.strftime("%Y-%m-%d"),
        "until": today.strftime("%Y-%m-%d")
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()

    pull_requests = response.json()
    return len(pull_requests)

def get_commit_file_contents(owner, repo, username, token, branch):
    base_url = "https://api.github.com"
    commits_url = f"{base_url}/repos/{owner}/{repo}/commits?sha={branch}"
    headers = {"Authorization": f"token {token}"}

    response = requests.get(commits_url, headers=headers)
    response.raise_for_status()

    commits_info = response.json()

    file_contents = {}
    for commit_info in commits_info:
        commit_sha = commit_info.get('sha')
        commit_files_url = f"{base_url}/repos/{owner}/{repo}/commits/{commit_sha}"
        commit_response = requests.get(commit_files_url, headers=headers)
        commit_response.raise_for_status()

        commit_data = commit_response.json()
        author = commit_data.get('author', {}).get('login')

        if author == username:
            modified_files = commit_data.get('files', {})

            for file_info in modified_files:
                file_path = file_info.get('filename')
                file_url = file_info.get('raw_url')
                file_content = get_file_content(file_url)

                if file_content is not None:
                    file_contents[file_path] = file_content

    return file_contents

def get_file_content(file_url):
    response = requests.get(file_url)
    if response.status_code == 200:
        return response.text
    else:
        return None



def generate(commit, pr, content_variables):
    llm_g = ChatGoogleGenerativeAI(model="gemini-pro", temperature=0.9)
    Developer_Performance_Analysis_Prompt = """
    Task: Evaluate the developer's performance by analyzing code quality and comments quality in their recent commits.

    Instructions:
    1. Provide the code content from the developer's last commit in the specified repository.
    2. Assess the code quality, looking at factors such as adherence to coding standards, maintainability, and efficiency.
    3. Evaluate the quality of comments in the code, considering clarity, completeness, and relevance.
    4. Provide a rating on a scale of 1 to 5 stars, where 1 represents poor performance and 5 represents excellent performance.
    5. Include a detailed summary of the analysis, highlighting strengths and areas for improvement.
    6. If there are specific criteria or guidelines used for the evaluation, mention them in your analysis.
    7. Offer constructive feedback on how the developer can enhance both code and comment quality.

    Example Input:
    Code from Last Commit: {code}

    Example Output:
    Rating: 1-5 stars
    Summary:
    - Code Quality: [Comments on code quality]
    - Comments Quality: [Comments on comments quality]
    - Strengths: [Identify strong points]
    - Areas for Improvement: [Highlight areas that need improvement]

    Note: A higher rating should reflect better overall performance in terms of code and comments quality also don't print code in your analysis.
    """

    Developer_Performance_Analysis_Prompt = Developer_Performance_Analysis_Prompt.format(code = content_variables, PR = pr, commit = commit)
    response = llm_g.invoke(Developer_Performance_Analysis_Prompt)
    response = response.content
    performance = response
    return performance


def get_github_repo_issues(owner, repo, token):
    issues_url = f'https://api.github.com/repos/{owner}/{repo}/issues'
    headers = {"Authorization": f"token {token}"}

    response = requests.get(issues_url, headers=headers)

    if response.status_code == 200:
        issues = response.json()
        return [issue['number'] for issue in issues]
    else:
        print(f"Failed to retrieve issues. Status code: {response.status_code}")
        return []

def get_github_issue_comments(owner, repo, issue_number, token):
    comments_url = f'https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}/comments'
    headers = {"Authorization": f"token {token}"}

    response = requests.get(comments_url, headers=headers)

    if response.status_code == 200:
        comments = response.json()
        for comment in comments:
            return comment['body']
    else:
        print(f"Failed to retrieve comments for issue #{issue_number}. Status code: {response.status_code}")
        return None









# url = "https://h49574215.atlassian.net/rest/api/2/issue/TES-1"
# email = "h49574215@gmail.com"
# api_token = "ATATT3xFfGF0p4hZOJ6rJ-sP8ZTLOBicXD07BFeSU47DleIhCkxScxDummtIuEYP6A3NlKfPwzFwG6YMrljTqbSx_58Xs2GfC2dCxI510o3sMK9Rjcf3Q3MflYOA9FZLdZhn4V5mNiilCwHCvNfr9tFHcMII36kcsxkDKBn6liW1T6zTkEZa_8M=6882AEE7"


def get_jira_issue_info(url,issue_key, email, api_token):
    # Jira API endpoint URL
    url = f"{url}/rest/api/2/issue/{issue_key}"

    # HTTP headers
    headers = {
        "Accept": "application/json",
    }

    # Make the API request
    response = requests.get(url, headers=headers, auth=(email, api_token))

    if response.status_code == 200:
        data = response.json()

        # Extract relevant information
        issue_key = data['key']
        issue_type = data['fields']['issuetype']['name']
        project_name = data['fields']['project']['name']
        priority_name = data['fields']['priority']['name']
        status_name = data['fields']['status']['name']
        summary = data['fields']['summary']
        creator_name = data['fields']['creator']['displayName']

        assignee_info = data['fields']['assignee']
        if assignee_info:
            assignee_name = assignee_info['displayName']
        else:
            assignee_name = "Unassigned"

        # Create a dictionary with the extracted information
        result = {
            "Issue Key": issue_key,
            "Issue Type": issue_type,
            "Project": project_name,
            "Priority": priority_name,
            "Status": status_name,
            "Summary": summary,
            "Creator": creator_name,
            "Assignee": assignee_name,
        }

        return result
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
