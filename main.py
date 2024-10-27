import datetime
import requests
import os
from xml.dom import minidom
import hashlib

# GitHub API headers
HEADERS = {'authorization': 'token ' + os.environ['ACCESS_TOKEN']}
user = os.environ['user']

def get_current_repo():
    query = '''
    query($login: String!) {
        user(login: $login) {
            repositories(first: 1, orderBy: {field: UPDATED_AT, direction: DESC}) {
                nodes {
                    nameWithOwner
                }
            }
        }
    }'''
    variables = {'login': user}
    response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=HEADERS)
    if response.status_code == 200:
        print("Repo: ",response.json()['data']['user']['repositories']['nodes'][0]['nameWithOwner'])
        return response.json()['data']['user']['repositories']['nodes'][0]['nameWithOwner']
    else:
        raise Exception('Failed to fetch current repo', response.status_code, response.text)

def get_languages():
    query = '''
    query($login: String!) {
        user(login: $login) {
            repositories(first: 100) {
                nodes {
                    languages(first: 5) {
                        edges {
                            node {
                                name
                            }
                        }
                    }
                }
            }
        }
    }'''
    variables = {'login': user}
    response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=HEADERS)
    if response.status_code == 200:
        languages = set()
        for repo in response.json()['data']['user']['repositories']['nodes']:
            for lang in repo['languages']['edges']:
                languages.add(lang['node']['name'])
        return ', '.join(languages)
    else:
        raise Exception('Failed to fetch languages', response.status_code, response.text)

def get_contributions():
    query = '''
    query($login: String!) {
        user(login: $login) {
            contributionsCollection {
                totalCommitContributions
                restrictedContributionsCount
                contributionCalendar {
                    totalContributions
                }
            }
        }
    }'''
    variables = {'login': user}
    response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()['data']['user']['contributionsCollection']
        return data['totalCommitContributions'], data['restrictedContributionsCount'], data['contributionCalendar']['totalContributions']
    else:
        raise Exception('Failed to fetch contributions', response.status_code, response.text)

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
    variables = {'login': user}
    response = requests.post('https://api.github.com/graphql', json={'query': query, 'variables': variables}, headers=HEADERS)
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

def update_svg(current_repo, languages, contributions, lines_added, lines_removed):
    svg = minidom.parse('template.svg')
    tspan = svg.getElementsByTagName('tspan')
    tspan[1].firstChild.data = f"Currently working on: {current_repo}"
    tspan[2].firstChild.data = f"Languages used: {languages}"
    tspan[3].firstChild.data = f"Total contributions: {contributions}"
    tspan[4].firstChild.data = f"Lines added: {lines_added}++"
    tspan[5].firstChild.data = f"Lines removed: {lines_removed}--"
    with open('svg-card.svg', 'w', encoding='utf-8') as f:
        f.write(svg.toxml())

if __name__ == '__main__':
    current_repo = get_current_repo()
    languages = get_languages()
    total_contributions, restricted_contributions, total_contributions_calendar = get_contributions()
    lines_added, lines_removed = get_total_loc()
    # update_svg(current_repo, languages, total_contributions, lines_added, lines_removed)
    print(current_repo, languages, total_contributions, lines_added, lines_removed)
