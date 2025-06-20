curl -X POST http://localhost:5000/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rep@example.com",
    "password": "secure123"
}'

curl -X POST http://localhost:5000/prospects \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "Jane Smith",
    "address": "456 Elm St",
    "count": 0,
    "list": "Prospects",
    "userEmail": "rep@example.com",
    "contactEmail": "jane@example.com",
    "contactPhone": "555-6789",
    "notes": "Met in the afternoon",
    "latitude": 41.5868,
    "longitude": -93.625
}'

curl -X POST http://localhost:5000/prospects/1/notes \
  -H "Content-Type: application/json" \
  -d '{
    "content": "She seemed interested in solar, follow-up next week.",
    "authorEmail": "rep@example.com"
}'

curl -X POST http://localhost:5000/prospects/1/knocks \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-06-21T10:15:00",
    "status": "Answered",
    "latitude": 41.5868,
    "longitude": -93.625,
    "userEmail": "rep@example.com"
}'