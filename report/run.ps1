param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]] $LabArgs
)

$labRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
if (-not $LabArgs) {
    $LabArgs = @('python', '-m', 'pytest')
}
& docker run --rm --mount "type=bind,source=$labRoot,target=/lab" lab-deepagents-local @LabArgs
if ($LASTEXITCODE -ne 0) {
    throw "Lab command failed (exit $LASTEXITCODE)."
}
