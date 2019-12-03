from unittest import TestCase
from ghia.github import GitHub
from betamax import Betamax
from betamax.cassette import cassette
import os
import pathlib
from ghia.common import GHIA,get_rules
import importlib
import pkg_resources



TOKEN_PLACEHOLDER = '<AUTH_TOKEN>'
TOKEN = os.getenv('GITHUB_TOKEN', default=TOKEN_PLACEHOLDER)

USER_PLACEHOLDER = 'USER_PLACEHOLDER'
USER = os.getenv('GITHUB_USER', default=USER_PLACEHOLDER)
TOKEN_HEADER = 'token ' + TOKEN

REPO = 'ghia_test_env'


def sanitize_token(interaction, current_cassette):
    headers = interaction.data['request']['headers']
    token = headers.get("Authorization")
    if token is None:
        return

    current_cassette.placeholders.append(
        cassette.Placeholder(placeholder=TOKEN_PLACEHOLDER, replace=token[0])
        )

    current_cassette.placeholders.append(
        cassette.Placeholder(placeholder=USER_PLACEHOLDER, replace=USER)
        )


def sanitize_before_playback(interaction, current_cassette):
    interaction.replace(USER_PLACEHOLDER,USER)

with Betamax.configure() as config:
    config.cassette_library_dir = pathlib.Path(__file__).parent / 'cassettes'
    config.define_cassette_placeholder(TOKEN_PLACEHOLDER, TOKEN_HEADER)
    config.before_record(callback=sanitize_token)
    config.before_playback(callback=sanitize_before_playback)


def configPath(name):
    return pathlib.Path(__file__).parent / 'rules' / name



class TestGit(TestCase):

    def test_list(self):
        github = GitHub(TOKEN)
        with Betamax(github.session).use_cassette('issues'):
            issues = github.issues(USER, REPO)
            assert len(issues) == 116


    def test_assign(self):
        github = GitHub(TOKEN)
        with Betamax(github.session).use_cassette('assignees'):
            github.set_issue_assignees(USER, REPO,124,[USER])
            issues = github.issues(USER, REPO, assignee=USER)
            for issue in issues:
                if issue['number'] == 124:
                    assert issue['assignees'][0]['login'] == USER
                    break

    def test_apply_rules(self):
        with open(configPath('rules.match_label.cfg'),'r') as conf:
            rules, fallback  = get_rules(None,None,conf)
            ghia = GHIA(TOKEN, rules, fallback, False, GHIA.DEFAULT_STRATEGY)

            with Betamax(ghia.github.session).use_cassette('test_apply_rules'):
                ghia.run(USER, REPO)
                issues = ghia.github.issues(USER, REPO, assignee=USER)
                assert len(issues) == 14





