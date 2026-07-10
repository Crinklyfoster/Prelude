import glob
import csv
import re

def main():
    report_lines = []
    report_lines.append("# LLM Benchmark Report Card")
    report_lines.append("")
    report_lines.append("This report summarizes the performance of the `/chat` endpoint (LLM generation) across different models and user loads.")
    report_lines.append("")
    report_lines.append("| Model | Users | Requests | Failures | Median (ms) | Avg (ms) | Req/s |")
    report_lines.append("|-------|-------|----------|----------|-------------|----------|-------|")

    # Find all stats files
    files = glob.glob("results_*_stats.csv")
    files.sort()

    for file in files:
        # Extract model and users from filename
        # Format: results_{model}_{users}users_stats.csv
        match = re.match(r"results_(.*)_(\d+)users_stats\.csv", file)
        if not match:
            continue
        
        model = match.group(1)
        users = match.group(2)

        with open(file, 'r') as f:
            reader = csv.DictReader(f)
            chat_row = None
            for row in reader:
                if row.get("Name") == "/chat" and row.get("Type") == "POST":
                    chat_row = row
                    break
            
            if chat_row:
                reqs = chat_row.get("Request Count", "0")
                fails = chat_row.get("Failure Count", "0")
                median = chat_row.get("Median Response Time", "0")
                avg = chat_row.get("Average Response Time", "0")
                req_s = chat_row.get("Requests/s", "0")
                
                report_lines.append(f"| {model} | {users} | {reqs} | {fails} | {median} | {avg} | {req_s} |")
    
    with open("benchmark_report.md", "w") as f:
        f.write("\n".join(report_lines) + "\n")
    
    print("\nReport card generated successfully at benchmarks/benchmark_report.md!")

if __name__ == "__main__":
    main()
