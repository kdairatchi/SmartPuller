import os
import subprocess
import tempfile
import json

class TargetScanner:
    def __init__(self, nuclei_path="nuclei", nmap_path="nmap"):
        self.nuclei_path = nuclei_path
        self.nmap_path = nmap_path

    def run_nuclei(self, targets, cve_id=None, template=None):
        results = {}
        with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
            for t in targets:
                f.write(t + "\n")
            f.flush()

            cmd = [
                self.nuclei_path,
                "-l", f.name,
                "-json"
            ]
            if cve_id:
                cmd += ["-t", f"cves/{cve_id}.yaml"]
            elif template:
                cmd += ["-t", template]

            try:
                output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL).decode("utf-8").splitlines()
                for line in output:
                    try:
                        data = json.loads(line)
                        target = data.get("host")
                        results[target] = data
                    except json.JSONDecodeError:
                        continue
            except subprocess.CalledProcessError as e:
                results["error"] = f"Nuclei failed: {e}"
        return results

    def run_nmap_vuln(self, ip_list):
        nmap_results = {}
        try:
            for ip in ip_list:
                cmd = [self.nmap_path, "-sV", "--script", "vuln", "-oX", "-", ip]
                output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
                nmap_results[ip] = output.decode()
        except Exception as e:
            nmap_results["error"] = str(e)
        return nmap_results

if __name__ == "__main__":
    scanner = TargetScanner()
    test_targets = ["https://example.com", "http://testphp.vulnweb.com"]
    print("\n[+] Running Nuclei Scan...")
    print(scanner.run_nuclei(test_targets, cve_id="CVE-2023-XXXX"))

    print("\n[+] Running Nmap Vuln Scan...")
    print(scanner.run_nmap_vuln(["93.184.216.34"]))  # Example IP

