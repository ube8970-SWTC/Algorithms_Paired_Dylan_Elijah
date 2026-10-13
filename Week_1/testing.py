
# working solution - Dylan

import json
import ast
from pathlib import Path


def load_tickets_from_file(file_path=None):
    if file_path is None:
        file_path = Path(__file__).with_name("data.txt")

    if not file_path.exists():
        return []

    text = file_path.read_text(encoding="utf-8").strip()
    if not text:
        return []

    try:
        data = ast.literal_eval(text.partition("=")[2].strip())
    except (SyntaxError, ValueError):
        return []

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    return []


def normalize_ticket(ticket):
    if not isinstance(ticket, dict):
        return {
            "ticket_id": "",
            "category": "",
            "status": "",
            "priority": "",
            "age_days": None,
        }

    return {
        "ticket_id": str(ticket.get("ticket_id") or ticket.get("id") or "").strip(),
        "category": str(ticket.get("category") or "").strip(),
        "status": str(ticket.get("status") or "").strip().lower(),
        "priority": str(ticket.get("priority") or "unknown").strip().lower(),
        "age_days": ticket.get("age_days"),
    }


def validate_ticket(ticket):
    normalized = normalize_ticket(ticket)

    if not isinstance(ticket, dict):
        return False, "Record is not a dictionary."

    missing_values = []
    if not normalized["ticket_id"]:
        missing_values.append("ticket_id")
    if not normalized["category"]:
        missing_values.append("category")
    if not normalized["status"]:
        missing_values.append("status")
    if normalized["age_days"] is None:
        missing_values.append("age_days")

    if missing_values:
        return False, "Missing or empty value(s): " + ", ".join(missing_values) + "."

    if (
        isinstance(normalized["age_days"], bool)
        or not isinstance(normalized["age_days"], int)
        or normalized["age_days"] < 0
    ):
        return False, "age_days must be a non-negative integer."

    if normalized["status"] not in {"open", "closed"}:
        return False, f"Status '{normalized['status']}' is not acceptable. Use 'open' or 'closed'."

    return True, normalized


def process_tickets(tickets):
    open_tickets = []
    records_needing_checking = []

    for index, ticket in enumerate(tickets, start=1):
        is_valid, result = validate_ticket(ticket)

        if not is_valid:
            records_needing_checking.append(
                {
                    "ticket_index": index,
                    "reason": result,
                    "raw_record": ticket,
                }
            )
            continue

        ticket_data = result
        if ticket_data["status"] == "open":
            open_tickets.append(
                {
                    "ticket_index": index,
                    "ticket_id": ticket_data["ticket_id"],
                    "category": ticket_data["category"],
                    "status": ticket_data["status"],
                    "priority": ticket_data["priority"],
                    "age_days": ticket_data["age_days"],
                }
            )

    no_matches = []
    if not open_tickets:
        no_matches.append(
            {
                "reason": "No valid open tickets were found. Either all valid tickets were closed, or records were missing required values and were moved to the checking list."
            }
        )

    return open_tickets, records_needing_checking, no_matches, len(tickets)


if __name__ == "__main__":
    tickets = load_tickets_from_file()

    if not tickets:
        print("No ticket data found in data.txt.")
        raise SystemExit

    open_tickets, records_needing_checking, no_matches, total_tickets = process_tickets(tickets)

    print(f"Total tickets checked: {total_tickets}")
    print()

    print("Open tickets:")
    if open_tickets:
        for ticket in open_tickets:
            print(
                f"  #{ticket['ticket_index']} | ID: {ticket['ticket_id']} | "
                f"Category: {ticket['category']} | Age: {ticket['age_days']} days | "
                f"Status: {ticket['status']} | Priority: {ticket['priority']}"
            )
    else:
        print("  No open tickets found.")
    print()

    print("Records needing checking:")
    if records_needing_checking:
        for item in records_needing_checking:
            print(f"  #{item['ticket_index']} | {item['reason']}")
    else:
        print("  None")
    print()

    print("No matching records:")
    if no_matches:
        for item in no_matches:
            print(f"  - {item['reason']}")
    else:
        print("  None")
