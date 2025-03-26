import os
import shodan
import zoomeye.sdk as zoomeye_sdk
from censys.search import CensysHosts
import fofa
import requests

class TargetFinder:
    def __init__(self, shodan_api_key=None, zoomeye_api_key=None, censys_api_id=None, censys_api_secret=None, fofa_email=None, fofa_key=None):
        self.shodan_api_key = shodan_api_key or os.getenv("SHODAN_API_KEY")
        self.zoomeye_api_key = zoomeye_api_key or os.getenv("ZOOMEYE_API_KEY")
        self.censys_api_id = censys_api_id or os.getenv("CENSYS_API_ID")
        self.censys_api_secret = censys_api_secret or os.getenv("CENSYS_API_SECRET")
        self.fofa_email = fofa_email or os.getenv("FOFA_EMAIL")
        self.fofa_key = fofa_key or os.getenv("FOFA_KEY")

        self.shodan_api = shodan.Shodan(self.shodan_api_key) if self.shodan_api_key else None
        self.zoomeye_api = zoomeye_sdk.ZoomEye(api_key=self.zoomeye_api_key) if self.zoomeye_api_key else None
        self.censys_api = CensysHosts(api_id=self.censys_api_id, api_secret=self.censys_api_secret) if self.censys_api_id and self.censys_api_secret else None
        self.fofa_client = fofa.Client(self.fofa_email, self.fofa_key) if self.fofa_email and self.fofa_key else None

    def search_shodan(self, query):
        if not self.shodan_api:
            return "Shodan API key not provided."
        try:
            results = self.shodan_api.search(query)
            return [match['ip_str'] for match in results['matches']]
        except shodan.APIError as e:
            return f"Shodan API Error: {e}"

    def search_zoomeye(self, query):
        if not self.zoomeye_api:
            return "ZoomEye API key not provided."
        try:
            self.zoomeye_api.dork_search(query)
            return [host['ip'] for host in self.zoomeye_api.dork_filter('ip')]
        except Exception as e:
            return f"ZoomEye API Error: {e}"

    def search_censys(self, query):
        if not self.censys_api:
            return "Censys API credentials not provided."
        try:
            results = self.censys_api.search(query)
            return [result['ip'] for result in results]
        except Exception as e:
            return f"Censys API Error: {e}"

    def search_fofa(self, query):
        if not self.fofa_client:
            return "FOFA API credentials not provided."
        try:
            data = self.fofa_client.get_data(query, 100)
            return [host[0] for host in data['results']]
        except Exception as e:
            return f"FOFA API Error: {e}"

    def search_all(self, query):
        results = {
            'shodan': self.search_shodan(query),
            'zoomeye': self.search_zoomeye(query),
            'censys': self.search_censys(query),
            'fofa': self.search_fofa(query)
        }
        return results

if __name__ == "__main__":
    finder = TargetFinder(
        shodan_api_key="your_shodan_api_key",
        zoomeye_api_key="your_zoomeye_api_key",
        censys_api_id="your_censys_api_id",
        censys_api_secret="your_censys_api_secret",
        fofa_email="your_fofa_email",
        fofa_key="your_fofa_api_key"
    )
    query = 'Apache httpd 2.4.49'
    results = finder.search_all(query)
    for platform, ips in results.items():
        print(f"{platform.upper()} Results:")
        if isinstance(ips, list):
            for ip in ips:
                print(f"- {ip}")
        else:
            print(f"- {ips}")

