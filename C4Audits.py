
import os
import requests
import json
from C4FindingsScraper import C4FindingsScraper

class C4Audits():

    def __init__(self):
        self.base_dir = "Code4rena"
        self.org = "code-423n4"
        self.user = ""
        self.api_url_template = "https://api.github.com/repos/##ORG##/##REPO##/issues/##ISSUE##"
        self.raw_url_template = "https://raw.githubusercontent.com/code-423n4/##REPO##/main/data/##USER##-##TYPE##.md"
        self.createDirIfNotExists(self.base_dir)

    def createDirIfNotExists(self, path):
        if not os.path.exists(path):
            os.makedirs(path)

    def processContests(self, all_findings):
        results = []
        for contest_data in all_findings:
            results.append(self.processContest(contest_data))
        return results

    def processQAGas(self, repo, name, issue, issue_text):
        type = "G"
        folder_name = "GAS"
        if issue_text.endswith("Q.md"):
            type = "Q"
            folder_name = "QA"
        url = self.raw_url_template.replace("##REPO##", repo).replace("##USER##", self.user).replace("##TYPE##", type)
        md = requests.get(url).text
        file_name = "README.md"
        path = os.path.join(self.base_dir, name, folder_name)
        self.createDirIfNotExists(path)
        additional = f"# Original link\n{issue}\n"
        with open(os.path.join(path, file_name), "w") as newFile:
            newFile.write(additional + md)
        return f"[[{folder_name}]]({os.path.join(folder_name, file_name)})"

    def getSeverityFromLables(self, data):
        severity = ""
        for label in data['labels']:
            if label["name"].startswith("3"):
                severity = "[HIGH]"
            elif label["name"].startswith("2"):
                severity = "[MEDIUM]"
            elif label["name"].startswith("QA"):
                severity = "[QA]"
        return severity

    def processHighMid(self, repo, name, issueNum, issue):
        url = self.api_url_template.replace("##ORG##", self.org).replace("##REPO##", repo).replace("##ISSUE##", issueNum)
        data = json.loads(requests.get(url).text)
        md = data['body']
        if f"{self.user}-Q" in md:
            return self.processQAGas(repo, name, issue, f"{self.user}-Q.md")
        elif f"{self.user}-G" in md:
            return self.processQAGas(repo, name, issue, f"{self.user}-G.md")
        original_title = data['title']
        title = original_title.replace(" ", "_").replace("/","-").replace("`","'")
        severity = self.getSeverityFromLables(data)
        folder_name = severity + "-" + title
        path = os.path.join(self.base_dir, name, folder_name)
        self.createDirIfNotExists(path)
        additional = f"# Original link\n{issue}\n"
        rel_link = os.path.join(folder_name, "README.md")
        with open(os.path.join(path, "README.md"), "w") as newFile:
            newFile.write(additional + md)
        return f"[{severity}]({rel_link}) - {original_title}"

    def processIssues(self, issues , name):
        results = []
        repo = issues[0].split(self.org + "/")[1].split("/")[0]
        for issue in issues:
            issueNum = issue.split("/")[-1]
            if issueNum.endswith("md"):
                result = self.processQAGas(repo, name, issue, issueNum)
            else:
                result = self.processHighMid(repo, name, issueNum, issue)
            results.append(result)
        return results

    def createContestREADME(self, results, name):
        str = f"# Findings for {name} \n\n"
        for result in results:
            str = str + "- " + result +"\n"
        with open(os.path.join(self.base_dir, name, "README.md"), "w") as f:
            f.write(str)

    def processContest(self, contest_data):
        for contest_name, issues in contest_data.items():
            self.createDirIfNotExists(os.path.join(self.base_dir, contest_name))
            results = self.processIssues(issues, contest_name)
            self.createContestREADME(results, contest_name)
            return (contest_name, len(results))

    def createC4Readme(self, results):
        str = f"# Findings in Code4rena \n\n"
        for result in results:
            str = str + "- " + f"{result[1]} [findings]({result[0]}/README.md) in {result[0]}" +"\n"
        with open(os.path.join(self.base_dir, "README.md"), "w") as f:
            f.write(str)

    def createC4(self, user):
        self.user = user
        crawler = C4FindingsScraper()
        all_findings = crawler.getUserFindings(user)
        results = self.processContests(all_findings)
        self.createC4Readme(results)
