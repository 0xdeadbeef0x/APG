


import json
import requests



class C4FindingsScraper():
    website_reports_url = "https://api.github.com/repos/code-423n4/code423n4.com/contents/_data/reports"

    def getAllReportsDownloadUrl(self):
        download_urls = set()
        reports = json.loads(requests.get(self.website_reports_url).text)
        for report_json in reports:
            if 'download_url' in report_json.keys():
                download_urls.add(report_json['download_url'])
        return download_urls

    def getUserFindings(self, user):
        download_urls = self.getAllReportsDownloadUrl()
        findings = []
        print(f"[+] Searching findings by {user}")
        for download_url in download_urls:
            result, name = self.getUserFindingsForReport(user, download_url)
            if result:
                print(f"    [-] Found {len(result[name])} findings in {name}")
                findings.append(result)
        return findings

    def getUserFindingsForReport(self, user, download_url):
        findings = None
        slug = "'"
        contest_json = json.loads(requests.get(download_url).text)
        if 'circa' in contest_json.keys() and 'title' in contest_json['circa'].keys() and 'html' in contest_json.keys():
            slug = contest_json['circa']['slug']
            issues = set()
            plain_html = contest_json['html']
            mentions_of_user = plain_html.split(f"{user}</a>")
            for mention in mentions_of_user:
                if mention.endswith('">'):
                    issueUrl = mention.split('<a href=\"')[-1][:-2]
                    if 'code-423n4' in issueUrl:
                        issues.add(issueUrl)
        if len(issues) > 0:
            findings = {}
            findings[slug] = list(issues)
        return findings, slug

