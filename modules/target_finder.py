import os
import shodan
from censys.search import CensysHosts
import requests

class TargetFinder:
    def __init__(self):
        self.shodan_key = os.getenv("SHODAN_API_KEY")
        self.censys_id = os.getenv("CENSYS_API_ID")
        self.censys_secret = os.getenv("CENSYS_API_SECRET")
        self.fofa_email = os.getenv("FOFA_EMAIL")
        self.fofa_key = os.getenv("FOFA_KEY")

        self.shodan = shodan.Shodan(self.shodan_key) if self.shodan_key else None
        self.censys = CensysHosts(api_id=self.censys_id, api_secret=self.censys_secret) if self.censys_id else None

    def search_shodan(self, query):
        if not self.shodan:
            return []
        try:
            results = self.shodan.search(query)
            return [match['ip_str'] for match in results['matches']]
        except Exception as e:
            return [f"Shodan error: {e}"]

    def search_censys(self, query):
        if not self.censys:
            return []
        try:
            res = self.censys.search(query=query, per_page=10)
            return [r['ip'] for r in res]
        except Exception as e:
            return [f"Censys error: {e}"]

    def search_fofa(self, query, size=10):
        if not self.fofa_email or not self.fofa_key:
            return []
        try:
            url = f"https://fofa.info/api/v1/search/all?email={self.fofa_email}&key={self.fofa_key}&qbase64={query}&size={size}"
            res = requests.get(url)
            return res.json().get("results", [])
        except Exception as e:
            return [f"FOFA error: {e}"]

    def collect_targets(self, cve_description):
        targets = {}
        try:
            if "Apache" in cve_description:
                dork = 'title:"Apache2 Ubuntu Default Page"'
            elif "Zimbra" in cve_description:
                dork = 'http.favicon.hash:1624375939'
            else:
                dork = cve_description[:100]

            targets["shodan"] = self.search_shodan(dork)
            targets["censys"] = self.search_censys(dork)
            return targets
        except Exception as e:
            return {"error": str(e)}
