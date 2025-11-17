#!/usr/bin/env python3
"""
Token Tracker
=============
Track and log API token usage and costs for embeddings and LLM calls.

Usage:
    # As a module
    from dev_tools.backend.token_tracker import TokenTracker

    tracker = TokenTracker()
    tracker.log_embedding(text="...", tokens=123, cost=0.0001)
    tracker.log_llm_call(prompt_tokens=2341, response_tokens=523, cost=0.02)
    tracker.summary()

    # As a CLI tool
    python dev-tools/backend/token_tracker.py
    python dev-tools/backend/token_tracker.py --summary
    python dev-tools/backend/token_tracker.py --export usage.csv

Features:
- Real-time tracking of API usage
- Daily/weekly/monthly summaries
- Cost projections
- Export usage data to CSV
- Budget alerts and warnings
- Persistent storage of usage logs
"""

import json
import csv
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict


@dataclass
class EmbeddingCall:
    """Record of an embedding API call."""
    timestamp: str
    text_length: int
    tokens: int
    cost: float
    model: str = "text-embedding-3-small"


@dataclass
class LLMCall:
    """Record of an LLM API call."""
    timestamp: str
    prompt_tokens: int
    response_tokens: int
    total_tokens: int
    cost: float
    model: str = "claude-sonnet-4-20250514"


class TokenTracker:
    """Track API token usage and costs."""

    # Pricing (as of Jan 2025)
    EMBEDDING_COST_PER_1K = 0.00002  # OpenAI text-embedding-3-small
    CLAUDE_INPUT_COST_PER_1M = 3.0    # Claude Sonnet 4
    CLAUDE_OUTPUT_COST_PER_1M = 15.0

    def __init__(self, log_file: Optional[str] = None):
        """
        Initialize the token tracker.

        Args:
            log_file: Path to log file (default: dev-tools/token_usage.json)
        """
        if log_file is None:
            log_file = str(Path(__file__).parent.parent / "token_usage.json")

        self.log_file = Path(log_file)
        self.embedding_calls: List[EmbeddingCall] = []
        self.llm_calls: List[LLMCall] = []

        # Load existing logs
        self.load_logs()

    def load_logs(self):
        """Load existing logs from file."""
        if not self.log_file.exists():
            return

        try:
            with open(self.log_file, 'r') as f:
                data = json.load(f)

            self.embedding_calls = [
                EmbeddingCall(**call) for call in data.get('embedding_calls', [])
            ]
            self.llm_calls = [
                LLMCall(**call) for call in data.get('llm_calls', [])
            ]
        except Exception as e:
            print(f"Warning: Could not load logs: {e}")

    def save_logs(self):
        """Save logs to file."""
        try:
            # Ensure directory exists
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'embedding_calls': [asdict(call) for call in self.embedding_calls],
                'llm_calls': [asdict(call) for call in self.llm_calls]
            }

            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save logs: {e}")

    def log_embedding(
        self,
        text: str = None,
        tokens: int = None,
        cost: float = None,
        text_length: int = None,
        model: str = "text-embedding-3-small"
    ):
        """
        Log an embedding API call.

        Args:
            text: The text that was embedded (optional)
            tokens: Number of tokens used
            cost: Cost of the call (optional, will be calculated if not provided)
            text_length: Length of text (optional, will be calculated from text)
            model: Model used
        """
        # Calculate text length
        if text_length is None:
            text_length = len(text) if text else 0

        # Estimate tokens if not provided
        if tokens is None:
            # Rough estimate: 1 token ≈ 4 characters for English, 3 for Icelandic
            tokens = int(text_length / 3) if text_length else 0

        # Calculate cost if not provided
        if cost is None:
            cost = (tokens / 1000) * self.EMBEDDING_COST_PER_1K

        call = EmbeddingCall(
            timestamp=datetime.now().isoformat(),
            text_length=text_length,
            tokens=tokens,
            cost=cost,
            model=model
        )

        self.embedding_calls.append(call)
        self.save_logs()

    def log_llm_call(
        self,
        prompt_tokens: int,
        response_tokens: int,
        cost: float = None,
        model: str = "claude-sonnet-4-20250514"
    ):
        """
        Log an LLM API call.

        Args:
            prompt_tokens: Number of prompt/input tokens
            response_tokens: Number of response/output tokens
            cost: Total cost (optional, will be calculated if not provided)
            model: Model used
        """
        total_tokens = prompt_tokens + response_tokens

        # Calculate cost if not provided
        if cost is None:
            input_cost = (prompt_tokens / 1_000_000) * self.CLAUDE_INPUT_COST_PER_1M
            output_cost = (response_tokens / 1_000_000) * self.CLAUDE_OUTPUT_COST_PER_1M
            cost = input_cost + output_cost

        call = LLMCall(
            timestamp=datetime.now().isoformat(),
            prompt_tokens=prompt_tokens,
            response_tokens=response_tokens,
            total_tokens=total_tokens,
            cost=cost,
            model=model
        )

        self.llm_calls.append(call)
        self.save_logs()

    def get_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get usage statistics for a date range.

        Args:
            start_date: Start date (default: beginning of time)
            end_date: End date (default: now)

        Returns:
            Dictionary with usage statistics
        """
        # Filter calls by date range
        embedding_calls = self.embedding_calls
        llm_calls = self.llm_calls

        if start_date:
            start_iso = start_date.isoformat()
            embedding_calls = [c for c in embedding_calls if c.timestamp >= start_iso]
            llm_calls = [c for c in llm_calls if c.timestamp >= start_iso]

        if end_date:
            end_iso = end_date.isoformat()
            embedding_calls = [c for c in embedding_calls if c.timestamp <= end_iso]
            llm_calls = [c for c in llm_calls if c.timestamp <= end_iso]

        # Calculate stats
        embedding_stats = {
            'calls': len(embedding_calls),
            'tokens': sum(c.tokens for c in embedding_calls),
            'cost': sum(c.cost for c in embedding_calls),
            'avg_tokens_per_call': sum(c.tokens for c in embedding_calls) / len(embedding_calls) if embedding_calls else 0
        }

        llm_stats = {
            'calls': len(llm_calls),
            'prompt_tokens': sum(c.prompt_tokens for c in llm_calls),
            'response_tokens': sum(c.response_tokens for c in llm_calls),
            'total_tokens': sum(c.total_tokens for c in llm_calls),
            'cost': sum(c.cost for c in llm_calls),
            'avg_prompt_tokens': sum(c.prompt_tokens for c in llm_calls) / len(llm_calls) if llm_calls else 0,
            'avg_response_tokens': sum(c.response_tokens for c in llm_calls) / len(llm_calls) if llm_calls else 0
        }

        total_cost = embedding_stats['cost'] + llm_stats['cost']

        return {
            'embedding': embedding_stats,
            'llm': llm_stats,
            'total_cost': total_cost
        }

    def summary(self, period: str = "today"):
        """
        Print usage summary.

        Args:
            period: Time period - "today", "week", "month", "all"
        """
        # Determine date range
        now = datetime.now()
        if period == "today":
            start_date = datetime(now.year, now.month, now.day)
            period_label = "Today"
        elif period == "week":
            start_date = now - timedelta(days=7)
            period_label = "Last 7 Days"
        elif period == "month":
            start_date = now - timedelta(days=30)
            period_label = "Last 30 Days"
        else:  # all
            start_date = None
            period_label = "All Time"

        stats = self.get_stats(start_date=start_date)

        print("\n" + "="*70)
        print(f"Token Usage Summary ({period_label})".center(70))
        print("="*70)

        # Embedding stats
        print("\nEmbeddings (OpenAI):")
        print(f"  Calls: {stats['embedding']['calls']:,}")
        print(f"  Tokens: {stats['embedding']['tokens']:,}")
        print(f"  Cost: ${stats['embedding']['cost']:.4f}")
        if stats['embedding']['calls'] > 0:
            print(f"  Avg tokens/call: {stats['embedding']['avg_tokens_per_call']:.0f}")

        # LLM stats
        print("\nLLM (Claude Sonnet 4):")
        print(f"  Calls: {stats['llm']['calls']:,}")
        print(f"  Prompt tokens: {stats['llm']['prompt_tokens']:,}")
        print(f"  Response tokens: {stats['llm']['response_tokens']:,}")
        print(f"  Total tokens: {stats['llm']['total_tokens']:,}")
        print(f"  Cost: ${stats['llm']['cost']:.4f}")
        if stats['llm']['calls'] > 0:
            print(f"  Avg prompt tokens/call: {stats['llm']['avg_prompt_tokens']:.0f}")
            print(f"  Avg response tokens/call: {stats['llm']['avg_response_tokens']:.0f}")

        # Total
        print("\n" + "-"*70)
        print(f"Total cost ({period_label.lower()}): ${stats['total_cost']:.4f}")

        # Projections
        if period == "today" and stats['total_cost'] > 0:
            monthly_projection = stats['total_cost'] * 30
            yearly_projection = stats['total_cost'] * 365
            print(f"\nProjections:")
            print(f"  Estimated monthly: ${monthly_projection:.2f}")
            print(f"  Estimated yearly: ${yearly_projection:.2f}")

        print("\n")

    def daily_breakdown(self, days: int = 7):
        """
        Show daily breakdown of usage.

        Args:
            days: Number of days to show
        """
        print("\n" + "="*70)
        print(f"Daily Breakdown (Last {days} Days)".center(70))
        print("="*70 + "\n")

        # Group calls by date
        daily_stats = defaultdict(lambda: {'embedding_cost': 0, 'llm_cost': 0})

        for call in self.embedding_calls:
            date = call.timestamp[:10]  # Extract date (YYYY-MM-DD)
            daily_stats[date]['embedding_cost'] += call.cost

        for call in self.llm_calls:
            date = call.timestamp[:10]
            daily_stats[date]['llm_cost'] += call.cost

        # Get last N days
        now = datetime.now()
        dates = [(now - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(days)]
        dates.reverse()

        # Print table
        print(f"{'Date':<12} {'Embedding':<12} {'LLM':<12} {'Total':<12}")
        print("-"*70)

        total_embedding = 0
        total_llm = 0

        for date in dates:
            stats = daily_stats[date]
            embedding_cost = stats['embedding_cost']
            llm_cost = stats['llm_cost']
            total = embedding_cost + llm_cost

            total_embedding += embedding_cost
            total_llm += llm_cost

            print(f"{date:<12} ${embedding_cost:<11.4f} ${llm_cost:<11.4f} ${total:<11.4f}")

        print("-"*70)
        print(f"{'Total':<12} ${total_embedding:<11.4f} ${total_llm:<11.4f} ${total_embedding + total_llm:<11.4f}")
        print("\n")

    def export_csv(self, filename: str):
        """
        Export usage data to CSV.

        Args:
            filename: Output CSV file path
        """
        filepath = Path(filename)

        try:
            with open(filepath, 'w', newline='') as csvfile:
                # Embedding calls
                writer = csv.writer(csvfile)
                writer.writerow(['Type', 'Timestamp', 'Tokens', 'Cost', 'Model', 'Extra'])

                for call in self.embedding_calls:
                    writer.writerow([
                        'embedding',
                        call.timestamp,
                        call.tokens,
                        f"{call.cost:.6f}",
                        call.model,
                        f"text_length={call.text_length}"
                    ])

                for call in self.llm_calls:
                    writer.writerow([
                        'llm',
                        call.timestamp,
                        call.total_tokens,
                        f"{call.cost:.6f}",
                        call.model,
                        f"prompt={call.prompt_tokens},response={call.response_tokens}"
                    ])

            print(f"\n✓ Usage data exported to: {filepath.absolute()}\n")
        except Exception as e:
            print(f"\n✗ Failed to export: {e}\n")

    def check_budget(self, daily_budget: float = 5.0, monthly_budget: float = 100.0):
        """
        Check if usage is within budget and show warnings.

        Args:
            daily_budget: Daily budget in USD
            monthly_budget: Monthly budget in USD
        """
        # Today's usage
        today_stats = self.get_stats(start_date=datetime.now().replace(hour=0, minute=0, second=0, microsecond=0))
        today_cost = today_stats['total_cost']

        # This month's usage
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_stats = self.get_stats(start_date=month_start)
        month_cost = month_stats['total_cost']

        print("\n" + "="*70)
        print("Budget Status".center(70))
        print("="*70 + "\n")

        # Daily budget
        daily_percent = (today_cost / daily_budget) * 100 if daily_budget > 0 else 0
        print(f"Daily Budget: ${today_cost:.4f} / ${daily_budget:.2f} ({daily_percent:.1f}%)")

        if daily_percent >= 100:
            print("  ⚠️  WARNING: Daily budget exceeded!")
        elif daily_percent >= 80:
            print("  ⚠️  WARNING: Approaching daily budget limit")
        elif daily_percent >= 50:
            print("  ⚡ Over half of daily budget used")
        else:
            print("  ✓ Within daily budget")

        # Monthly budget
        monthly_percent = (month_cost / monthly_budget) * 100 if monthly_budget > 0 else 0
        print(f"\nMonthly Budget: ${month_cost:.4f} / ${monthly_budget:.2f} ({monthly_percent:.1f}%)")

        if monthly_percent >= 100:
            print("  ⚠️  WARNING: Monthly budget exceeded!")
        elif monthly_percent >= 80:
            print("  ⚠️  WARNING: Approaching monthly budget limit")
        elif monthly_percent >= 50:
            print("  ⚡ Over half of monthly budget used")
        else:
            print("  ✓ Within monthly budget")

        print("\n")

    def reset_logs(self):
        """Clear all logs."""
        self.embedding_calls = []
        self.llm_calls = []
        self.save_logs()
        print("\n✓ Logs cleared\n")


def main():
    """Main CLI interface."""
    import argparse

    parser = argparse.ArgumentParser(description="Token usage tracker and analyzer")
    parser.add_argument('--summary', action='store_true', help='Show usage summary')
    parser.add_argument('--period', choices=['today', 'week', 'month', 'all'], default='today',
                        help='Time period for summary')
    parser.add_argument('--daily', action='store_true', help='Show daily breakdown')
    parser.add_argument('--days', type=int, default=7, help='Number of days for daily breakdown')
    parser.add_argument('--budget', action='store_true', help='Check budget status')
    parser.add_argument('--export', type=str, metavar='FILE', help='Export usage to CSV')
    parser.add_argument('--reset', action='store_true', help='Clear all logs')

    args = parser.parse_args()

    tracker = TokenTracker()

    if args.reset:
        confirm = input("Are you sure you want to clear all logs? (yes/no): ")
        if confirm.lower() == 'yes':
            tracker.reset_logs()
        return

    if args.export:
        tracker.export_csv(args.export)
        return

    if args.daily:
        tracker.daily_breakdown(days=args.days)
        return

    if args.budget:
        tracker.check_budget()
        return

    # Default: show summary
    tracker.summary(period=args.period)


if __name__ == "__main__":
    main()
