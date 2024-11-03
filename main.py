import requests
import random
import os

# GitHub API headers
HEADERS = {'authorization': 'bearer ' + os.environ['GH_TOKEN']}
user = os.environ['user']

def request_call(query):
    variables =  {'login': user}
    response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=HEADERS)
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
        return response.json()['data']['user']['repositories']['nodes'][0]['nameWithOwner'], response.json()['data']['user']['repositories']['nodes'][0]['url']
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
        return response.json()['data']['viewer']['repositories']['totalCount']
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

$$\space \space \space \space \space \space \space$$[![Portfolio](https://img.shields.io/badge/netlify-%23000000.svg?style=for-the-badge&logo=netlify&logoColor=#00C7B7)](https://shishir-ashok.netlify.app/) </br>
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/shshir-ashok) [![Medium](https://img.shields.io/badge/Medium-00AB6C?style=flat&logo=medium&logoColor=white&color=000000)](https://shishirashok.medium.com/)

---

## 🌟 About Me
I'm a data science enthusiast transitioning from a network engineering background. With over 3 years of experience in automating workflows and optimizing secure infrastructures, I'm now diving deep into the world of data science.

| Attribute          | Details                                                                 |
|--------------------|-------------------------------------------------------------------------|
| 🎓 **Education**   | Pursuing a Master's in Data Science and Analytics at Maynooth University|
| 🌐 **Portfolio**   | [Check out my work](https://shishir-ashok.netlify.app/)                 |
| 📫 **Contact**     | [shishir.ashoka@gmail.com](mailto:shishir.ashoka@gmail.com)             |

---

## 📊 GitHub Stats

| **Metric**                  | **Stats**                                           |
| --------------------------- | --------------------------------------------------- |
| 🛠️ **Current Project**     | [{current_repo}]({url_current_repo})                |
| 📂 **Total Repos**         | {repo_count}                                        |
| 📝 **Lines of Code**       | {total_contributions:,} ($$\\color{{\#2dba4e}}{lines_added:,}++ \space \space \space \\color{{\#f0440a}}{lines_removed:,}--$$)                        |

---

## 🤝 Let’s Connect!

I love connecting with fellow data enthusiasts, professionals, and learners. Whether you have questions, insights, or just want to chat data, feel free to reach out! </br>

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/shshir-ashok) [![Medium](https://img.shields.io/badge/Medium-00AB6C?style=flat&logo=medium&logoColor=white&color=000000)](https://shishirashok.medium.com/) </br>
$$\space \space \space \space \space \space \space$$[![Portfolio](https://img.shields.io/badge/netlify-%23000000.svg?style=for-the-badge&logo=netlify&logoColor=#00C7B7)](https://shishir-ashok.netlify.app/)
    """

    # Write the content to README.md
    with open("README.md", "w", encoding='utf-8') as file:
        file.write(readme_content)


if __name__ == '__main__':
    
    current_repo, url_current_repo = get_current_repo()
    repo_count = get_repo_count()
    lines_added, lines_removed = get_total_loc()
    total_contributions = lines_added + lines_removed
    
    print(repo_count, current_repo, url_current_repo, total_contributions, lines_added, lines_removed)
    update_readme(current_repo, url_current_repo, repo_count, lines_added, lines_removed, total_contributions)    
