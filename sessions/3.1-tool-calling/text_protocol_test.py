"""Session 3.1, step 2: how often can our three-word parser read the model's first reply?

It sends four real-looking customer messages, five times each, with the same text
protocol, and checks only the first reply: is it exactly one CALL line that our
parser can split into three words?
"""
from text_protocol import client, MODEL, SYSTEM

MESSAGES = {
    "Sara": "Hi, this is Sara. The airline cancelled my flight to Lisbon. "
            "My booking is NT-4821. Can I get my money back?",
    "John": "Hello, John here. I changed my mind about my Rome hotel, booking NT-5107. "
            "Can I cancel it and get a refund?",
    "Tom": "Hi, Tom again. My booking number is NT 5307. Can you move my Rome hotel "
           "two days later? Also, is breakfast included?",
    "Lukas": "Hi, this is Lukas. I have two trips with you, NT-6190 to Paris and "
             "NT-6244 to Madrid. Are both still OK after the airline strike?",
}


def check(text):
    """Our parser from text_protocol.py: CALL, the tool name, the booking ID."""
    if not text.startswith("CALL "):
        return "no CALL at the start"
    try:
        _, name, booking_id = text.split()
    except ValueError:
        return "CALL line, but not three words"
    return f"OK, parsed {name} {booking_id}"


if __name__ == "__main__":
    ok = total = 0
    for who, message in MESSAGES.items():
        for _ in range(5):
            text = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "system", "content": SYSTEM},
                          {"role": "user", "content": message}],
            ).choices[0].message.content
            result = check(text)
            ok += result.startswith("OK")
            total += 1
            print(f"{who:13} | {result:32} | {text!r}")
    print(f"Our parser could read {ok} of {total} first replies.")
