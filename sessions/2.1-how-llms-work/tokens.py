"""Session 2.1: how a model sees Sara's message. It counts the tokens and shows each piece."""
import tiktoken

MESSAGE = ("Hi, this is Sara. The airline cancelled my flight to Lisbon. "
           "My booking is NT-4821. Can I get my money back?")

enc = tiktoken.encoding_for_model("gpt-4o-mini")  # the tokenizer of gpt-4o-mini
ids = enc.encode(MESSAGE)                          # text -> token numbers

print(f"Characters: {len(MESSAGE)}")
print(f"Words:      {len(MESSAGE.split())}")
print(f"Tokens:     {len(ids)}\n")
for i in ids:                                      # each token number and its piece of text
    print(f"{i:>7}  {enc.decode([i])!r}")
