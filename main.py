"""make.fun bounty entry: "A Day of One-Line Pitches".

Writes one original one-line pitch to /output/entry.txt (or
./output/entry.txt when /output is not writable). Pure stdlib,
deterministic: the same pitch is written on every run.
"""

import os
import re
import sys

# The pitch: one sentence, plain words, written to convince a friend
# who has never coded to let an AI agent build their first app idea
# on make.fun. Original work, written for this entry.
PITCH = (
    "That app idea you keep saying you'll build one day \u2014 "
    "just describe it on make.fun today and you'll have a real "
    "working version to try tonight, no code, free to try, and "
    "nothing to lose if it's not right."
)

MIN_CHARS = 1
MAX_CHARS = 240

# Jargon a non-coder friend should never have to decode. The pitch
# must not contain any of these words.
JARGON = {
    "api", "sdk", "deploy", "deployment", "repository", "repo",
    "framework", "algorithm", "blockchain", "token", "smart contract",
    "backend", "frontend", "compile", "compiler", "database",
    "kubernetes", "docker", "server", "endpoint", "graphql",
}

# Words longer than this are suspicious in a plain-words pitch.
MAX_WORD_LEN = 14

# A pitch that reads in one breath: cap the word count so the point
# lands without the friend having to re-read.
MAX_WORDS = 45

# The pitch must give the friend a concrete reason to say yes NOW,
# not someday: it must name today or tonight.
NOW_WORDS = {"today", "tonight"}


def _sentence_terminators(text):
    """Count sentence-ending punctuation marks in the text.

    A terminator only counts when it ends the text or is followed by
    whitespace -- the dot inside "make.fun" is not one.
    """
    return len(re.findall(r"[.!?](?=\s|$)", text))


def validate_pitch(text):
    """Validate the pitch against the competition gate and judge brief.

    Raises ValueError with a clear message on the first failure.
    Returns the validated text unchanged.
    """
    if not isinstance(text, str):
        raise ValueError("pitch must be a string")
    if not text.strip():
        raise ValueError("pitch must not be blank or only whitespace")
    if text != text.strip():
        raise ValueError("pitch must not have leading or trailing whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("pitch must be a single line")
    n = len(text)
    if n < MIN_CHARS or n > MAX_CHARS:
        raise ValueError(
            "pitch is %d characters; gate requires %d-%d"
            % (n, MIN_CHARS, MAX_CHARS)
        )
    # Exactly one sentence: exactly one sentence terminator, at the end.
    if _sentence_terminators(text) != 1:
        raise ValueError("pitch must be exactly one sentence")
    if text[-1] not in ".!?":
        raise ValueError("pitch must end with sentence punctuation")
    # Plain words: no jargon, no very long words, no shouting.
    words = re.findall(r"[A-Za-z][A-Za-z']*", text)
    if not words:
        raise ValueError("pitch contains no words")
    if len(words) > MAX_WORDS:
        raise ValueError(
            "pitch has %d words; one read should take at most %d"
            % (len(words), MAX_WORDS)
        )
    lowered = [w.lower() for w in words]
    if not (set(lowered) & NOW_WORDS):
        raise ValueError("pitch must give a concrete reason to say yes now")
    bad = sorted(set(lowered) & JARGON)
    if bad:
        raise ValueError("pitch contains jargon: %s" % ", ".join(bad))
    long_words = [w for w in words if len(w) > MAX_WORD_LEN]
    if long_words:
        raise ValueError("pitch contains over-long words: %s" % ", ".join(long_words))
    if any(w.isupper() and len(w) > 1 for w in words):
        raise ValueError("pitch must not contain ALL-CAPS words")
    # The pitch must name the place where the idea gets built.
    if "make.fun" not in text:
        raise ValueError("pitch must mention make.fun")
    # Must be valid UTF-8 (the gate requires UTF-8 text).
    text.encode("utf-8")
    return text


def _write_pitch(path, pitch):
    """Write the pitch to path; return True on success."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(pitch)
    return True


def main():
    pitch = validate_pitch(PITCH)
    preferred = os.path.join(os.sep, "output", "entry.txt")
    fallback = os.path.join(".", "output", "entry.txt")
    try:
        _write_pitch(preferred, pitch)
        path = preferred
    except OSError:
        _write_pitch(fallback, pitch)
        path = fallback
    print("wrote %d characters to %s" % (len(pitch), path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
