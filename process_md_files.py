import os
import re

# === CONFIG ===
folder_path = os.path.dirname(os.path.abspath(__file__))  # Use script's current folder
phone_number = "(877)-635-7391"
link = "https://potta-potty-7391.netlify.app"

# === REGEX ===
phone_regex = re.compile(r"\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
markdown_link_pattern = re.compile(r"\[📞.*?\]\(.*?\)")
special_chars_pattern = re.compile(r"[^\w\s\-\(\)]", re.UNICODE)
cta_check_pattern = re.compile(r"Call Now:.*?☎️💧")

# === CLEAN + HTML CTA FUNCTION ===
def transform_markdown(content):
    lines = content.splitlines()
    output = []
    title_processed = False
    cta_inserted = False
    first_h2_done = False

    for line in lines:
        if re.match(r"^#+\s*$", line) or re.match(r"^#+\s*[-#\s]+$", line):  # Skip junk headers
            continue
        if output and output[-1] == "" and line.strip() == "":
            continue
        if cta_check_pattern.search(line) or re.match(r"#+\s*&nbsp;+", line):
            continue

        if not title_processed and not line.strip().startswith("#"):
            clean_title = markdown_link_pattern.sub(phone_number, line)
            clean_title = special_chars_pattern.sub("", clean_title).strip()
            clean_title = phone_regex.sub(f"[📞 {phone_number}]({link})", clean_title)
            output.append(f"# {clean_title}")
            output.append("")

            if not cta_inserted:
                html_cta = (
                    f'<p align="center" style="font-size: 1.2em; font-weight: bold; margin: 20px 0;">\n'
                    f'  <a href="{link}" target="_blank" style="color: #007BFF; text-decoration: none;">📞 Call Now: {phone_number} ☎️💧</a>\n'
                    f'</p>'
                )
                output.append(html_cta)
                output.append("")
                cta_inserted = True

            title_processed = True
            continue

        if not first_h2_done and line.strip().startswith("##"):
            line = phone_regex.sub("", line)
            first_h2_done = True

        line = markdown_link_pattern.sub(phone_number, line)
        line = phone_regex.sub(f"[📞 {phone_number}]({link})", line)
        output.append(line)

    return "\n".join(output)

# === FILE PROCESSOR ===
def process_all_md_files():
    files = [f for f in os.listdir(folder_path) if f.endswith(".md")]
    print(f"📁 Found {len(files)} Markdown files.\n")

    updated_count = 0

    for filename in files:
        path = os.path.join(folder_path, filename)
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.strip():
                print(f"⚠️ Skipped empty file: {filename}")
                continue

            updated = transform_markdown(content)

            with open(path, "w", encoding="utf-8") as f:
                f.write(updated)

            print(f"✅ Updated: {filename}")
            updated_count += 1

        except Exception as e:
            print(f"❌ Error in {filename}: {e}")

    print(f"\n🎉 Done. Updated {updated_count} file(s) out of {len(files)}.")

# === MAIN ===
if __name__ == "__main__":
    process_all_md_files()
