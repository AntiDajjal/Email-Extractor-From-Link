import argparse
import re
import requests
from urllib.parse import urlparse
import sys

def is_valid_email(email):
    """Check if the email is valid using a simple regex pattern."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def extract_emails_from_url(url):
    """Extract emails from a given URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        content = response.text
        emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        return list(set(filter(is_valid_email, emails)))
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return []

def process_links(input_file, output_file=None, verbose=True):
    """Process links from the input file and extract emails."""
    all_emails = []

    with open(input_file, 'r') as f:
        links = f.read().splitlines()

    total_links = len(links)
    for i, link in enumerate(links, 1):
        if verbose:
            print(f"Processing link {i}/{total_links}: {link}")

        parsed_url = urlparse(link)
        if not parsed_url.scheme:
            link = f"http://{link}"

        emails = extract_emails_from_url(link)
        all_emails.extend(emails)

        if verbose:
            print(f"Found {len(emails)} email(s) from {link}")
            for email in emails:
                print(f"  - {email}")
            print()

    unique_emails = list(set(all_emails))

    if output_file:
        with open(output_file, 'w') as f:
            for email in unique_emails:
                f.write(f"{email}\n")
        if verbose:
            print(f"Emails saved to {output_file}")

    if verbose:
        print(f"\nTotal unique emails found: {len(unique_emails)}")

    return unique_emails

def main():
    parser = argparse.ArgumentParser(description="Extract emails from links in a bulk file.")
    parser.add_argument("input_file", help="Input file containing links (one per line)")
    parser.add_argument("-o", "--output", help="Output file to save extracted emails")
    parser.add_argument("-q", "--quiet", action="store_true", help="Run in quiet mode (no verbose output)")
    args = parser.parse_args()

    process_links(args.input_file, args.output, verbose=not args.quiet)

if __name__ == "__main__":
    main()
