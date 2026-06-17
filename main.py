"""
main.py
CLI entry point — run the pipeline directly from the terminal without
needing the dashboard. Useful for testing and demos.

Usage:
    python main.py                          # uses built-in sample data
    python main.py path/to/your_file.csv   # uses your own CSV
"""

import sys
import json

from agents.supervisor import run_supervisor

# Built-in sample transactions for quick testing
SAMPLE_CSV = """Date,Description,Amount
2026-06-01,Starbucks,-8.50
2026-06-02,Walmart,-95.20
2026-06-03,Netflix,-15.99
2026-06-04,Spotify,-12.00
2026-06-05,Salary,2500.00
2026-06-06,Uber Eats,-22.15
2026-06-07,Starbucks,-9.00
2026-06-08,Amazon,-65.00
2026-06-09,Uber Eats,-18.50
2026-06-10,Gym Membership,-40.00
2026-06-11,Starbucks,-8.50
2026-06-12,Walmart,-112.00
2026-06-13,Uber Eats,-30.00
"""


def main():
    # Allow passing a CSV file path as a CLI argument
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
        print(f"[main] Reading from: {csv_path}")
        with open(csv_path, "r") as f:
            csv_content = f.read()
    else:
        print("[main] No CSV file provided — using built-in sample data.")
        csv_content = SAMPLE_CSV

    print("\n" + "="*60)
    print("  PERSONAL FINANCE AI — PIPELINE START")
    print("="*60 + "\n")

    # Run the full multi-agent pipeline via the Supervisor
    results = run_supervisor(csv_content)

    # Print the headline metrics
    metrics = results["report"]["metrics"]
    print("\n" + "="*60)
    print("  FINANCIAL OVERVIEW")
    print("="*60)
    print(f"  Monthly Income   : ${metrics['income']:>10,.2f}")
    print(f"  Monthly Expenses : ${metrics['expenses']:>10,.2f}")
    print(f"  Remaining Balance: ${metrics['remaining']:>10,.2f}")
    print(f"  Savings Rate     : {metrics['savings_rate']:>10.1f}%")
    print(f"  Top Category     : {metrics['top_category']}")
    print(f"  Annual Savings   : ${metrics['annual_savings']:>10,.2f}")
    print("="*60)

    # Print the full report
    print("\n📄 FINANCIAL HEALTH REPORT\n")
    print(results["report"]["report_markdown"])

    print("\n[main] ✓ Done. Launch the dashboard for interactive charts:")
    print("        streamlit run ui/dashboard.py")


if __name__ == "__main__":
    main()
