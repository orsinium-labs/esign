from argparse import ArgumentParser
import json
import requests
from urllib.parse import urlparse, parse_qs

URL_DIALOG = "https://nico-lab.atlassian.net/plugins/servlet/ac/esign/issue-sign-dialog"
URL_SIGN = "https://japi.esign-app.com/jira/api/sign-issue"


def get_jwt(token) -> str:
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': f'cloud.session.token={token}',
        'Origin': 'https://nico-lab.atlassian.net',
        'Referer': 'https://nico-lab.atlassian.net/',
        'Sec-Ch-Ua': '" Not A;Brand";v="99", "Chromium";v="96"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Linux"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',  # noqa
        'X-Requested-With': 'XMLHttpRequest',
    }
    ctx = json.dumps({
        "project.key": "NICO",
        "project.id": "10032",
        "issue.id": "14880",
        "issue.key": "NICO-1610",
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
    r = requests.post(URL_DIALOG, headers=headers, data=form)
    r.raise_for_status()
    url = urlparse(r.json()["url"])
    return parse_qs(url.query)["jwt"][0]


def sign(args):
    jwt = get_jwt(args.token)
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
    parser.add_argument('--meaning', default="Code Review")
    parser.add_argument('--title', default="Software Engineer")
    args = parser.parse_args()
    print(f"signing {args.meaning} for {args.issue}")
    sign(args)
    print("  signed!")


if __name__ == '__main__':
    main()
