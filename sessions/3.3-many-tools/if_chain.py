"""Session 3.3, step 1: picking the function with an if/elif chain (the old way)."""
from nova_tools import find_booking, get_refund_rules, prepare_refund

def run_tool(name, args):
    if name == "find_booking":
        return find_booking(**args)
    elif name == "get_refund_rules":
        return get_refund_rules()
    elif name == "prepare_refund":
        return prepare_refund(**args)
    # every new tool needs two more lines here

print(run_tool("find_booking", {"booking_id": "NT-7012"}))
print(run_tool("get_policy", {"topic": "pets"}))  # a tool we forgot to add
