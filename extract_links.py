import re

def extract_job_links(file_path):
    # Detect encoding and read
    encodings = ['utf-16', 'utf-8', 'cp1252']
    content = ""
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                content = f.read()
            break
        except:
            continue

    # Remove the ANSI terminal noise (the [0m stuff)
    content = re.sub(r'\x1b\[[0-9;]*m', '', content)

    # 1. Look for ALL URLs in the raw logs
    # This captures everything starting with http inside the Tavily JSON blocks
    all_raw_urls = re.findall(r'https?://[^\s"\'\}]+', content)
    
    # 2. Filter for Indeed and Naukri specifically
    recovered_links = []
    for link in all_raw_urls:
        # We look for Indeed or Naukri domains
        if "indeed.com" in link.lower() or "naukri.com" in link.lower():
            # Clean trailing punctuation that might have been caught by regex
            clean_link = link.rstrip('.,)')
            if clean_link not in recovered_links:
                recovered_links.append(clean_link)

    print("\n" + "="*50)
    print("      🔍 JOB LINK RECOVERY (INDEED & NAUKRI)")
    print("="*50)

    if not recovered_links:
        print("❌ No Indeed or Naukri links found in the logs yet.")
        print("Make sure you have run 'crewai run' with the updated search tool.")
    else:
        print(f"✅ Found {len(recovered_links)} FULL Job URLs:")
        for i, link in enumerate(recovered_links, 1):
            print(f"  {i}. {link}")
            
    # Save them to a clean file for your 'Apply' step
    with open("RECOVERED_LINKS.txt", "w", encoding='utf-8') as f:
        f.write("\n".join(recovered_links))
    
    print(f"\n📄 Saved to 'RECOVERED_LINKS.txt'")

if __name__ == "__main__":
    # Ensure you are pointing to your log file
    extract_job_links("project_output.log")