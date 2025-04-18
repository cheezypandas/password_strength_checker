Password Strength was designed as a lightweight, local tool that evaluated the strength of a password in a way that was both practical and a little thought-provoking. It didn’t just assign arbitrary scores — it gave context. How long would this password actually hold up under brute-force conditions? Had it already been exposed in a breach somewhere out in the wild? Password Strength aimed to answer those questions instantly, in plain language.

The interface was built using Python’s built-in tkinter library, chosen for its simplicity and wide compatibility. No frameworks, no fluff — just a clean, minimal GUI that made it easy to test and learn. Everything ran locally. There was no password logging, no remote storage. Privacy came baked in by default.

Behind the scenes, the app analyzed each password's entropy based on its character set — whether it used lowercase letters, uppercase letters, numbers, symbols, or some combination of them. From this entropy, the total number of possible combinations was calculated, and a cracking time estimate was produced based on modern brute-force speeds. The result? A rough, but useful, estimate of how resilient the password might be when facing off against a determined attacker.

Breach checking was handled via the HaveIBeenPwned API using the k-anonymity model. Only the first five characters of the SHA-1 hash of the password were sent to the API, ensuring that no complete hash or password ever left the user’s machine. Results were then matched locally to determine if the password had shown up in any known breaches — a clear and powerful indicator of reuse and risk.

The visual feedback was designed to be quick and human-readable. Strong passwords displayed encouraging results in green. Weak or breached ones triggered red warnings, complete with the number of times they appeared in public breach data. Even estimated cracking times were converted into plain English — from "instantly" to "230 years" — because raw entropy numbers don’t mean much without context.

Password Strength wasn’t built to replace password managers or serve enterprise-scale audits. It was meant as a hands-on, informative tool — the kind of thing a user could open up in a spare moment and walk away from with a better understanding of what makes a password truly strong. Lightweight in code but heavy on clarity, it fit neatly into the philosophy of "teach through feedback."

The tool required only Python 3 and a single external library — requests — which was used to interact with the breach-check API. A simple pip install requests was all that was needed to get started. The script itself ran with a single command: python password_gui.py.

Password Strength was released under the MIT License and remains freely available for modification and reuse. Its core goal was education through transparency, and its design made that easy to extend or repurpose for future experiments in personal or professional cybersecurity projects.
