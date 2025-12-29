$ErrorActionPreference = "Stop"

Write-Host "Waiting 2 seconds..."
Start-Sleep -Seconds 2

try {
    Write-Host "1. Registering/Verifying User..."
    $regUrl = "http://localhost:5000/api/auth/register/patient"
    $regBody = @{
        fullName = "Test User"
        email = "22-101136@students.eui.edu.eg"
        password = "12345678"
        dob = "1990-01-01"
        gender = "Male"
        conditionCategory = "None"
    } | ConvertTo-Json
    
    try {
        $regResp = Invoke-RestMethod -Uri $regUrl -Method Post -Body $regBody -ContentType "application/json"
        Write-Host "   Registration OK."
    } catch {
        if ($_.Exception.Response.StatusCode -eq 409) {
            Write-Host "   User already registered (expected)."
        } else {
             Write-Host "   Registration Failed: $($_.Exception.Message)"
             # Continue to login anyway
        }
    }

    Write-Host "2. Attempting Login..."
    $loginUrl = "http://localhost:5000/api/auth/login"
    $body = @{
        email = "22-101136@students.eui.edu.eg"
        password = "12345678"
    } | ConvertTo-Json
    
    $loginResp = Invoke-RestMethod -Uri $loginUrl -Method Post -Body $body -ContentType "application/json"
    $token = $loginResp.access_token
    Write-Host "   Login OK. Token: $($token.Substring(0, 15))..."

    Write-Host "`n3. Testing Protected Endpoint (Start Interview)..."
    $startUrl = "http://localhost:5000/api/consultation/start"
    $headers = @{
        Authorization = "Bearer $token"
        "Content-Type" = "application/json"
    }
    $startBody = @{
         message = "Hello test"
    } | ConvertTo-Json
    
    try {
        $startResp = Invoke-RestMethod -Uri $startUrl -Method Post -Headers $headers -Body $startBody
        Write-Host "   Success! Response: $($startResp | ConvertTo-Json -Depth 2)"
    } catch {
        Write-Host "   Request Failed. Status: $($_.Exception.Response.StatusCode)"
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $respBody = $reader.ReadToEnd()
        Write-Host "   Response Body: $respBody"
    }

} catch {
    Write-Host "Fatal Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        Write-Host "Response: $($reader.ReadToEnd())"
    }
}
