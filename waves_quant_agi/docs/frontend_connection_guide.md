🌐 docs/frontend_connection_guide.md – How the frontend connects and what it needs

📘 Plain English Explanation:
This is the manual for frontend developers so they can safely and correctly connect to your backend system.

What Frontend Needs to Know:
Use the JWT token (like a digital pass) from Supabase to make API calls

Send the token in every request for security

Use WebSockets for live updates (e.g., when profit/loss changes in real time)

Connect to deposit/withdraw APIs properly

Display strategies, NAV (Net Asset Value), and performance on dashboards

Example API Call:
http
Copy
Edit
GET /api/routes/portfolio
Authorization: Bearer <supabase_token>
Frontend Must Include:
Supabase login system

Strategy interface

Portfolio display

Deposit/withdraw features

Admin-only controls for premium users

📌 Why This Matters (Even If You're Not a Developer)
This documentation ensures any team member can onboard fast — devs, testers, even investors

Makes debugging easier when something breaks

Prevents confusion when growing your system or adding features

Makes handing off work to frontend/mobile teams smooth and mistake-free