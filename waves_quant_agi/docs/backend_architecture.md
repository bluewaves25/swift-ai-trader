🏗 docs/backend_architecture.md – How the system is structured (folders and logic)

📘 Plain English Explanation:
This document describes the folder layout and logic behind each folder.

Think of this as the blueprint or house plan of your project.

Folder Roles:
api/ → Entry gate; handles all requests from outside

engine/ → The smart trading brain (strategies, intelligence, validators)

core/ → Database models (who owns what, how much, etc.)

services/ → External tools like payment, messages, websocket

utils/ → Helper files, reusable checks

scripts/ → Setup scripts for launching or resetting stuff

config/ → Settings, logging, environment variables

tests/ → Where automated tests will live