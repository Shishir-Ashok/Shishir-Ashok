import datetime
import requests
import os
from xml.dom import minidom
import hashlib

# GitHub API headers
HEADERS = {'authorization': 'token ' + os.environ['ACCESS_TOKEN']}
user = os.environ['user']


def request_call(query):
    variables =  {'login': user}
    response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables, headers=HEADERS})
    return response
    
def get_current_repo():
    query = '''
    query($login: String!) {
        user(login: $login) {
            repositories(first: 1, orderBy: {field: UPDATED_AT, direction: DESC}) {
                nodes {
                    nameWithOwner 
                    url 
                }
            }
        }
    }
    '''
    response = request_call(query)
    if response.status_code == 200:
        print("Repo: ",response.json())
        return response.json()['data']['user']['repositories']['nodes'][0]['nameWithOwner'], response.json()['url']
        # return response.json()['data']['user']['repositories']['nodes'][0]['nameWithOwner']
    else:
        raise Exception('Failed to fetch current repo', response.status_code, response.text)

def get_repo_count():
    query = '''
    query {
      viewer {
        repositories {
          totalCount
        }
      }
    }
    '''
    response = request_call(query)
    if response.status_code == 200:
        print("Repo: ",response.json())
        return response.json()
    else:
        raise Exception('Failed to fetch repo count', response.status_code, response.text)

def recursive_loc(owner, repo_name, addition_total=0, deletion_total=0, cursor=None):
    query = '''
    query ($repo_name: String!, $owner: String!, $cursor: String) {
        repository(name: $repo_name, owner: $owner) {
            defaultBranchRef {
                target {
                    ... on Commit {
                        history(first: 100, after: $cursor) {
                            edges {
                                node {
                                    additions
                                    deletions
                                    author {
                                        user {
                                            login
                                        }
                                    }
                                }
                            }
                            pageInfo {
                                endCursor
                                hasNextPage
                            }
                        }
                    }
                }
            }
        }
    }'''
    variables = {'repo_name': repo_name, 'owner': owner, 'cursor': cursor}
    response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()['data']['repository']['defaultBranchRef']['target']['history']
        for edge in data['edges']:
            if edge['node']['author']['user'] and edge['node']['author']['user']['login'] == user:
                addition_total += edge['node']['additions']
                deletion_total += edge['node']['deletions']
        if data['pageInfo']['hasNextPage']:
            return recursive_loc(owner, repo_name, addition_total, deletion_total, data['pageInfo']['endCursor'])
        else:
            return addition_total, deletion_total
    else:
        raise Exception('Failed to fetch LOC data', response.status_code, response.text)

def get_total_loc():
    query = '''
    query($login: String!) {
        user(login: $login) {
            repositories(first: 100) {
                nodes {
                    nameWithOwner
                }
            }
        }
    }'''
    response = request_call(query)
    if response.status_code == 200:
        addition_total, deletion_total = 0, 0
        for repo in response.json()['data']['user']['repositories']['nodes']:
            owner, repo_name = repo['nameWithOwner'].split('/')
            additions, deletions = recursive_loc(owner, repo_name)
            addition_total += additions
            deletion_total += deletions
        return addition_total, deletion_total
    else:
        raise Exception('Failed to fetch repositories', response.status_code, response.text)

# This is your Python script that updates your README.md file with fresh data.

def update_readme(current_repo, url_current_repo, repo_count, lines_added, lines_removed, total_contributions):
    # Define the markdown content as a formatted string
    readme_content = f"""
# 👋 Hello! I'm Shishir

[![LinkedIn](https://img.shields.io/badge/-LinkedIn?style=social&logo=linkedin)](https://linkedin.com/in/shshir-ashok) [![Medium](https://img.shields.io/badge/-Medium?style=social&logo=medium)](https://shishirashok.medium.com/)
---

### 📝 About Me
Transitioning to data science, I bring 3+ years of experience as a network engineer specializing in automating workflows and optimizing secure infrastructures. 
With strong skills in data automation and analysis, I aim to leverage my technical expertise in a data-focused role.

- 🎓 I’m currently pursuing Data Science and Analytics master's degree at Maynooth University.
<!-- - 🌐 [My Personal Website](https://yourwebsite.com) -->
- 📫 How to reach me: [shishir.ashoka@gmail.com](mailto:shishir.ashoka@gmail.com)

---

### 📊 GitHub Stats
Recent Contribution: [{current_repo}]({url_current_repo}) | Repos : {repo_count) | Lines of Code: {total_contributions}(<span style="color: #00FF00;">`{lines_added}`</span>, <span style="color: #FF6347;">`{lines_removed}`</span>)
[Top Languages](https://github-readme-stats.vercel.app/api/top-langs/?username={user}&layout=compact&theme=radical)
---

![Views Counter](https://views-counter.vercel.app/badge?pageId=yourusername%2Frepository-name) 
"""

    # Write the content to README.md
    with open("README.md", "w") as file:
        file.write(readme_content)


if __name__ == '__main__':
    current_repo, url_current_repo = get_current_repo()
    repo_count = get_repo_count()
    lines_added, lines_removed = get_total_loc()
    total_contributions = lines_added + lines_removed
    print(repo_count, current_repo, url_current_repo, languages, total_contributions, lines_added, lines_removed)
    update_readme(current_repo, url_current_repo, repo_count, lines_added, lines_removed, total_contributions)    
