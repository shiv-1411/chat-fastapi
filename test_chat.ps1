$baseUrl = "http://localhost:8080/api/v1"

Write-Host "`n=== Testing Chat System with MongoDB ===`n"

# 1. Create first message
Write-Host "1. Creating first message..."
$body = @{
    user_id = "user1"
    message = "Hello! How are you?"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$baseUrl/chats" -Method Post -Headers @{"Content-Type"="application/json"} -Body $body
Write-Host "Response: $($response | ConvertTo-Json)"
$conversation_id = $response.conversation_id

# 2. Create second message in same conversation
Write-Host "`n2. Creating second message in same conversation..."
$body = @{
    user_id = "user2"
    message = "I'm doing great! How about you?"
    conversation_id = $conversation_id
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "$baseUrl/chats" -Method Post -Headers @{"Content-Type"="application/json"} -Body $body
Write-Host "Response: $($response | ConvertTo-Json)"

# 3. Get conversation
Write-Host "`n3. Getting conversation..."
$response = Invoke-RestMethod -Uri "$baseUrl/chats/$conversation_id" -Method Get
Write-Host "Conversation: $($response | ConvertTo-Json -Depth 10)"

# 4. Get user1's chat history
Write-Host "`n4. Getting user1's chat history..."
$response = Invoke-RestMethod -Uri "$baseUrl/users/user1/chats" -Method Get
Write-Host "User1's messages: $($response | ConvertTo-Json -Depth 10)"

# 5. Get user2's chat history
Write-Host "`n5. Getting user2's chat history..."
$response = Invoke-RestMethod -Uri "$baseUrl/users/user2/chats" -Method Get
Write-Host "User2's messages: $($response | ConvertTo-Json -Depth 10)"

# 6. Delete conversation
Write-Host "`n6. Deleting conversation..."
$response = Invoke-RestMethod -Uri "$baseUrl/chats/$conversation_id" -Method Delete
Write-Host "Delete response: $($response | ConvertTo-Json)"

# 7. Verify conversation is deleted
Write-Host "`n7. Verifying conversation is deleted..."
try {
    $response = Invoke-RestMethod -Uri "$baseUrl/chats/$conversation_id" -Method Get
} catch {
    Write-Host "Response status: $($_.Exception.Response.StatusCode.value__)"
}

Write-Host "`n=== Test Complete ===" 