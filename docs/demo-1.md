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

curl -X POST http://localhost:5000/customers \
  -H "Content-Type: application/json" \
  -d '{
    "fullName": "John Buyer",
    "address": "789 Maple Ave",
    "count": 1,
    "userEmail": "rep@example.com",
    "contactEmail": "john@example.com",
    "contactPhone": "555-0000",
    "notes": "Signed up last week",
    "latitude": 41.5890,
    "longitude": -93.6210
}'

curl -X POST http://localhost:5000/customers/1/notes \
-H "Content-Type: application/json" \
-d '{
  "content": "Customer signed up today.",
  "authorEmail": "rep@example.com"
}'

curl -X POST http://localhost:5000/customers/1/knocks \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-06-21T14:30:00",
    "status": "Answered",
    "latitude": 41.5890,
    "longitude": -93.6210,
    "userEmail": "rep@example.com"
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

curl -X POST http://localhost:5000/prospects/1/knocks \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-06-21T10:15:00",
    "status": "Answered",
    "latitude": 41.5868,
    "longitude": -93.625,
    "userEmail": "rep@example.com"
}'

curl -X POST http://localhost:5000/trips \
  -H "Content-Type: application/json" \
  -d '{
    "id": "a14d7cfc-e2b3-4f12-a123-ffcb00a1a934",
    "userEmail": "rep@example.com",
    "startAddress": "123 Main St",
    "endAddress": "456 Oak Ave",
    "miles": 4.2,
    "date": "2025-06-21T09:00:00"
}'

curl -X POST http://localhost:5000/trips \
  -H "Content-Type: application/json" \
  -d '{
    "id": "a14d7cfc-e2b3-4f12-a123-ffcb00a1a935",
    "userEmail": "rep@example.com",
    "startAddress": "123 Main St",
    "endAddress": "456 Oak Ave",
    "miles": 4.2,
    "date": "2025-06-21T09:00:00"
}'