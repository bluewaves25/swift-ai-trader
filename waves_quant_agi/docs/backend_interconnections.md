 docs/backend_interconnections.md – How all parts work together
 
📘 Plain English Explanation:
This file explains how each module talks to others inside the system.

It’s like the map of conversations between your team members — who hands off what to whom.

Example:
The frontend sends a request like "Get portfolio info"

The API receives it and passes it to the service layer

The service checks if the user is logged in

Then it asks the engine if trades need to run

Engine might activate a strategy → create a trade signal → send it to broker

Once the trade is done, the result is saved and sent back to the user

There’s even a diagram to show the flow visually.