from Data import TICKETS


# def validate_tickets(tickets):
#     for ticket in tickets:
#         if not isinstance(ticket, dict):
#             return False
#         if "ticket_id" not in ticket or "status" not in ticket or "category" not in ticket or "age_days" not in ticket or "priority" not in ticket:
#             return False
#         if not isinstance(ticket["ticket_id"], str) or not isinstance(ticket["status"], str) or not isinstance(ticket["category"], str) or not isinstance(ticket["age_days"], (int, type(None), bool)) or not isinstance(ticket["priority"], str):
#             return False
#     return True
## my original validate_tickets function is commented out above
# if __name__ == "__main__":
#     print(validate_tickets(TICKETS))
def normalize_ticket(ticket):
    if not isinstance(ticket, dict):
        return {
            "ticket_id": "",
            "category": "",
            "status": "",
            "priority": "",
            "age_days": None,
            "tag": "",
        }

    return {
        "ticket_id": str(ticket.get("ticket_id") or ticket.get("id") or "").strip(),
        "category": str(ticket.get("category") or "").strip(),
        "status": str(ticket.get("status") or "").strip().lower(),
        "priority": str(ticket.get("priority") or "unknown").strip().lower(),
        "age_days": ticket.get("age_days"),
        "tag": str(ticket.get("tag") or "").strip(),
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

    if normalized["status"] == "open" and normalized["age_days"] >= 2:
        if "follow-up" not in normalized["tag"].lower():
            normalized["tag"] = f"{normalized['tag']}, follow-up" if normalized["tag"] else "follow-up"

    return True, normalized

def select_open_tickets(tickets):
    open_tickets = []
    for index, ticket in enumerate(tickets, start=1):
        is_valid, result = validate_ticket(ticket)
        if is_valid and result["status"] == "open":
            result["ticket_index"] = index
            open_tickets.append(result)
    return open_tickets

# found an issue where the ticket numbers started with zero instead of 1 which needed to be corrected by using start=1 in enumerate.

def show_report(tickets):
    report = {
        "valid": 0,
        "invalid": 0,
        "invalid_tickets": []
    }
    for ticket in tickets:
        is_valid, result = validate_ticket(ticket)
        if is_valid:
            report["valid"] += 1
        else:
            report["invalid"] += 1
            report["invalid_tickets"].append(result)
    return report

if __name__ == "__main__":
    open_tickets = select_open_tickets(TICKETS)
    report = show_report(TICKETS)
    # print(f"Valid tickets: {report['valid']}")
    # changed print output to make it look nicer.
    print("Open tickets:")
    if open_tickets:
        for ticket in open_tickets:
            tag_text = f" | Tag: {ticket['tag']}" if ticket["tag"] else ""
            print(
                f"  #{ticket['ticket_index']} | ID: {ticket['ticket_id']} | "
                f"Category: {ticket['category']} | Age: {ticket['age_days']} days | "
                f"Status: {ticket['status']} | Priority: {ticket['priority']}"
                f"{tag_text}"
            )
    else:
        print("  No open tickets found.")
    print()
    print(f"Invalid tickets: {report['invalid']}")
    print("Records needing checking:")
    records_needing_checking = []
    for index, ticket in enumerate(TICKETS, start=1):
        is_valid, result = validate_ticket(ticket)
        if not is_valid:
            records_needing_checking.append({"ticket_index": index, "reason": result})

    if records_needing_checking:
        for item in records_needing_checking:
            print(f"  #{item['ticket_index']} | {item['reason']}")
    else:
        print("  None")
    print()