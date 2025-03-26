import os
import json
from datetime import datetime

class ReportBuilder:
    def __init__(self, output_dir="reports"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_markdown(self, cve_id, cve_desc, groq_summary, pocs, targets, medium=None):
        now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        md = f"# 🔥 CVE Report: {cve_id}\n"
        md += f"- 📅 Generated: `{now}`\n\n"
        md += f"## 🐞 CVE Description\n{cve_desc}\n\n"
        md += f"## 🤖 Groq AI Summary\n{groq_summary}\n\n"

        if medium:
            md += f"## ✍️ Related Medium Writeup\n"
            md += f"- **Title**: {medium.get('title')}\n"
            md += f"- **Tags**: {', '.join(medium.get('tags', []))}\n"
            md += f"- **URL**: {medium.get('url')}\n"
            md += f"- **Groq Insight**: {medium.get('insight')}\n\n"

        md += "## 📦 Proof of Concepts\n"
        if pocs:
            for source, urls in pocs.items():
                md += f"### {source.title()}:\n"
                for url in urls:
                    md += f"- {url}\n"
        else:
            md += "No public PoCs found.\n"

        md += "\n## 🌐 Live Targets Found\n"
        if targets:
            for engine, entries in targets.items():
                md += f"### {engine.title()}:\n"
                if isinstance(entries, list):
                    for ip in entries[:10]:
                        md += f"- {ip}\n"
                else:
                    md += f"- {entries}\n"
        else:
            md += "No targets detected.\n"

        filename = os.path.join(self.output_dir, f"{cve_id.replace('/', '_')}.md")
        with open(filename, "w") as f:
            f.write(md)
        return filename

    def generate_json(self, cve_id, cve_desc, groq_summary, pocs, targets, medium=None):
        data = {
            "cve_id": cve_id,
            "generated": datetime.utcnow().isoformat(),
            "description": cve_desc,
            "groq_summary": groq_summary,
            "pocs": pocs,
            "targets": targets,
            "medium": medium
        }
        filename = os.path.join(self.output_dir, f"{cve_id.replace('/', '_')}.json")
        with open(filename, "w") as f:
            json.dump(data, f, indent=2)
        return filename

if __name__ == "__main__":
    builder = ReportBuilder()
    cve = "CVE-2025-29927"
    summary = "This CVE allows bypassing middleware auth on Next.js."
    groq = "Middleware header spoofing vulnerability allowing unauthorized access."
    pocs = {
        "github": ["https://github.com/user/CVE-2025-29927-poc"],
        "exploitdb": []
    }
    targets = {
        "shodan": ["192.0.2.1", "198.51.100.5"],
        "censys": []
    }
    medium_data = {
        "title": "Next.js Middleware Hack",
        "url": "https://freedium.cfd/nextjs-hack",
        "tags": ["next.js", "x-middleware"],
        "insight": "Exploit used `x-middleware-subrequest` header injection."
    }

    builder.generate_markdown(cve, summary, groq, pocs, targets, medium_data)
    builder.generate_json(cve, summary, groq, pocs, targets, medium_data)

