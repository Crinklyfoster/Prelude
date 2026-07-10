import glob
import csv
import re

def get_provider(model):
    if "gemini" in model.lower():
        return "Gemini"
    elif "llama" in model.lower() or "groq" in model.lower():
        return "Groq"
    else:
        return "Ollama"

def format_time(val_str):
    try:
        val = float(val_str)
        if val >= 1000:
            return f"{val/1000:.1f} s"
        return f"{val:.0f} ms"
    except ValueError:
        return val_str

def main():
    report_lines = []
    report_lines.append("# LLM Benchmark Report Card")
    report_lines.append("")
    report_lines.append("This report summarizes the performance of the `/chat` endpoint (LLM generation) across different models.")
    report_lines.append("")
    report_lines.append("| Provider | Model | Avg Latency | P95 | Requests | Failures |")
    report_lines.append("|----------|-------|-------------|-----|----------|----------|")

    # Find all stats files
    files = glob.glob("results_*_stats.csv")
    files.sort()

    for file in files:
        # Extract model
        match_users = re.match(r"results_(.*)_(\d+)users_stats\.csv", file)
        match_no_users = re.match(r"results_(.*)_stats\.csv", file)
        
        if match_users:
            model = match_users.group(1)
        elif match_no_users:
            model = match_no_users.group(1)
        else:
            continue
            
        # Standardize model names for display
        model = model.replace("-", ":", 1) # Just in case it was converted to dash for filename
        
        provider = get_provider(model)

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
                p95 = format_time(chat_row.get("95%", "0"))
                avg = format_time(chat_row.get("Average Response Time", "0"))
                
                report_lines.append(f"| {provider} | {model} | {avg} | {p95} | {reqs} | {fails} |")
    
    with open("benchmark_report.md", "w") as f:
        f.write("\n".join(report_lines) + "\n")
    
    print("\nReport card generated successfully at benchmarks/benchmark_report.md!")

if __name__ == "__main__":
    main()
