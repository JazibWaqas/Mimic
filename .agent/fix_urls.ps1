$content = Get-Content "c:\Users\OMNIBOOK\Documents\GitHub\Mimic\frontend\app\vault\page.tsx" -Raw
$content = $content -replace 'src=\{`http://localhost:8000\$\{', 'src={`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}${'
Set-Content "c:\Users\OMNIBOOK\Documents\GitHub\Mimic\frontend\app\vault\page.tsx" -Value $content
Write-Host "✅ Fixed hardcoded URLs in vault/page.tsx"
