import os
import re

DISCLAIMER = """*IMPORTANT **Disclaimer:**\n\nThis site [Github.com] is a free service to assist homeowners in connecting with local service providers. All contractors/providers are independent and [Github.com] does not warrant or guarantee any work performed. It is the responsibility of the homeowner to verify that the hired contractor furnishes the necessary license and insurance required for the work being performed. All persons depicted in a photo or video are actors or models and not contractors listed on this site [Github.com]."""

OLD_REPO_URL = "https://github.com/allyoucaneatsushiin/plumbing-texas/blob/main/"
NEW_REPO_URL = "https://github.com/allyoucaneatsushiin/porta-potty/blob/main/"

STATE_CODES = {
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
}

def extract_city_service(filename):
    parts = filename.replace('.md', '').split('-')
    for i, part in enumerate(parts):
        if part.upper() in STATE_CODES:
            if i >= 2:
                city = parts[i - 1]
                service = ' '.join(parts[:i - 1])
                return service.strip(), city.strip()
    return None, None

def keyword_from_filename(filename):
    parts = filename.replace('.md', '').split('-')
    for i, part in enumerate(parts):
        if part.upper() in STATE_CODES:
            if i >= 2:
                city = parts[i - 1]
                service = ' '.join(parts[:i - 1])
                return f"{service} {city} {part.upper()}"
    return filename.replace('.md', '')

def build_internal_links(current_file, service, city, all_pages_info, max_links=4):
    links = []
    same_city = [p for p in all_pages_info if p["city"] == city and p["filename"] != current_file]

    if len(same_city) >= max_links:
        links = same_city[:max_links]
    else:
        links.extend(same_city)
        remaining = max_links - len(links)
        same_service = [
            p for p in all_pages_info
            if p["service"] == service and p["filename"] != current_file and p not in links
        ]
        links.extend(same_service[:remaining])

    markdown_links = "\n".join([
        f"- [{p['keyword']}]({NEW_REPO_URL}{p['filename']})" for p in links
    ])
    return markdown_links

def process_markdown_files():
    all_files = [f for f in os.listdir('.') if f.lower().endswith('.md')]
    print(f"📄 Found {len(all_files)} markdown files.")

    all_pages_info = []

    for filename in all_files:
        service, city = extract_city_service(filename)
        if service and city:
            keyword = keyword_from_filename(filename)
            all_pages_info.append({
                "filename": filename,
                "service": service,
                "city": city,
                "keyword": keyword
            })
            print(f"✅ Parsed: {filename} ➜ service: '{service}', city: '{city}'")
        else:
            print(f"⚠️ Skipped: {filename} (couldn't extract service/city)")

    for page in all_pages_info:
        try:
            file_path = page["filename"]
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace old repo links
            content = content.replace(OLD_REPO_URL, NEW_REPO_URL)

            # Remove old disclaimers (more flexible)
            content = re.sub(
                r"\*+IMPORTANT\s+\*+Disclaimer:.*?\[Github\.com\]\.\s*",
                "", content, flags=re.DOTALL | re.IGNORECASE
            )
            content = re.sub(
                r"\*+Disclaimer:.*?\[Github\.com\]\.\s*",
                "", content, flags=re.DOTALL | re.IGNORECASE
            )

            # Remove old Internal Links section
            content = re.sub(
                r"## Internal Links\s*- \[.*?\)\s*",
                "", content, flags=re.DOTALL
            )

            # Append disclaimer
            content += f"\n\n{DISCLAIMER}\n"

            # Add internal links
            internal_links = build_internal_links(page["filename"], page["service"], page["city"], all_pages_info)
            if internal_links:
                content += f"\n## Internal Links\n{internal_links}\n"

            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f"✅ Updated: {file_path}")
        except Exception as e:
            print(f"❌ Failed to process {file_path}: {e}")

if __name__ == "__main__":
    process_markdown_files()
