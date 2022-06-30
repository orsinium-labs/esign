from argparse import ArgumentParser
import json
import re
import requests
import sys
from urllib.parse import urlparse, parse_qs

URL_DIALOG = "https://{company}.atlassian.net/plugins/servlet/ac/esign/issue-sign-dialog"
URL_SIGN = "https://japi.esign-app.com/jira/api/sign-issue"
URL_FINALIZE = "https://japi.esign-app.com/jira/api/finalize-issue"
REX_ISSUE = re.compile(r'[A-Z]+\-[0-9]+')


def get_jwt(args) -> str:
    headers = {'Cookie': f'cloud.session.token={args.token}'}
    ctx = json.dumps({
        "project.key": args.issue.split('-')[0],
        "project.id": "0",
        "issue.id": "0",
        "issue.key": args.issue,
        "issuetype.id": "0",
    })
    form = {
        'plugin-key': 'esign',
        'product-context': ctx,
        'key': 'issue-sign-dialog',
        'width': '100%',
        'height': '100%',
        'classifier': 'json',
    }
    r = requests.post(URL_DIALOG.format(company=args.company), headers=headers, data=form)
    r.raise_for_status()
    url = urlparse(r.json()["url"])
    return parse_qs(url.query)["jwt"][0]


def sign(jwt: str, args) -> None:
    body = dict(
        issueKey=args.issue,
        meaning=args.meaning,
        pin=args.pin,
        title=args.title,
    )
    params = dict(issueKey=args.issue, jwt=jwt)
    r = requests.post(URL_SIGN, params=params, json=body)
    r.raise_for_status()
    assert r.status_code == 200


def finalize(jwt: str, args) -> None:
    body = dict(
        issueKey=args.issue,
        archiveFlag=True,
    )
    params = dict(issueKey=args.issue, jwt=jwt)
    r = requests.post(URL_FINALIZE, params=params, json=body)
    r.raise_for_status()
    assert r.status_code == 200


def main() -> int:
    parser = ArgumentParser()
    parser.add_argument('--issue', required=True, help="key of the issue to sign")
    parser.add_argument('--pin', required=True, help="pin as you enter it in esign form")
    parser.add_argument('--token', required=True, help="value of cloud.session.token cookie")
    parser.add_argument('--company', required=True, help="subdomain of atlassian.net to use")
    parser.add_argument('--meaning', default="Code Review", help="value for 'meaning' field")
    parser.add_argument('--title', default="Software Engineer", help="value for 'title' field")
    parser.add_argument('--finalize', action="store_true", help="set to finalize the signature")
    args = parser.parse_args()
    if not REX_ISSUE.fullmatch(args.issue):
        print(f'invalid issue: {args.issue}')
        return 1
    print(f"signing {args.meaning} for {args.issue}")
    jwt = get_jwt(args)
    sign(jwt, args)
    print("  signed!")
    if args.finalize:
        finalize(jwt, args)
        print("  finalized!")
    return 0


if __name__ == '__main__':
    sys.exit(main())
