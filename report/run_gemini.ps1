param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $LabArgs
)

$labRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if (-not $LabArgs) {
    $LabArgs = @('python', 'report/continue_gemini.py', 'all', '--recursion-limit', '60')
}
& docker run --rm --name lab-gemini-safe --mount "type=bind,source=$labRoot,target=/host/lab" lab-deepagents-local python /host/lab/report/secure_run.py @LabArgs
if ($LASTEXITCODE -ne 0) {
    throw "Gemini lab command failed (exit $LASTEXITCODE); observations were saved."
}
