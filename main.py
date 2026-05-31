import sys
from github_api import fetch_github_stats
from svg_generator import render_svgs

def main():
    # You can pass the username as a command line argument, e.g., `python main.py octocat`
    target_username = sys.argv[1] if len(sys.argv) > 1 else "torvalds" 
    
    print(f"Fetching GitHub data for {target_username}...")
    try:
        stats = fetch_github_stats(target_username)
        print("Data fetched successfully. Generating SVGs...")
        outputs = render_svgs(stats)
        for output_path in outputs:
            print(f"Generated: {output_path}")
    except Exception as e:
        print(f"Error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()