from argparse import ArgumentParser
import json
import requests
from urllib.parse import urlparse, parse_qs

URL_DIALOG = "https://{company}.atlassian.net/plugins/servlet/ac/esign/issue-sign-dialog"
URL_SIGN = "https://japi.esign-app.com/jira/api/sign-issue"


def get_jwt(args) -> str:
    headers = {'Cookie': f'cloud.session.token={args.token}'}
    ctx = json.dumps({
        "project.key": args.issue.split('-')[0],
        "project.id": "10032",
        "issue.id": "14880",
        "issue.key": args.issue,
        "issuetype.id": "10110",
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


def sign(args):
    jwt = get_jwt(args)
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


def main():
    parser = ArgumentParser()
    parser.add_argument('--issue', required=True)
    parser.add_argument('--pin', required=True)
    parser.add_argument('--token', required=True, help="value of cloud.session.token cookie")
    parser.add_argument('--company', default="nico-lab")
    parser.add_argument('--meaning', default="Code Review")
    parser.add_argument('--title', default="Software Engineer")
    args = parser.parse_args()
    print(f"signing {args.meaning} for {args.issue}")
    sign(args)
    print("  signed!")


if __name__ == '__main__':
    main()
