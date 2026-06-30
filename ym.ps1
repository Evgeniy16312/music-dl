# Yandex Music download wrapper (URL from arg, clipboard, or prompt)
$ErrorActionPreference = 'Stop'
$Root = $PSScriptRoot

function Get-YandexMusicUrl {
    param([string]$Text)
    if ([string]::IsNullOrWhiteSpace($Text)) { return $null }
    $Text = $Text.Trim().Trim('"').Trim("'")
    if ($Text -match 'https?://music\.yandex\.[a-z.]+/\S+') {
        return $Matches[0].TrimEnd('.,;)')
    }
    if ($Text -match 'music\.yandex\.[a-z.]+/\S+') {
        return ('https://' + $Matches[0].TrimEnd('.,;)'))
    }
    return $null
}

$url = Get-YandexMusicUrl (($args -join ' '))
if (-not $url) {
    try {
        $url = Get-YandexMusicUrl (Get-Clipboard -Raw)
    } catch {
        $url = $null
    }
}
while (-not $url) {
    Write-Host 'Paste Yandex Music URL (Ctrl+V) and press Enter:'
    $input = Read-Host
    $url = Get-YandexMusicUrl $input
    if (-not $url -and -not [string]::IsNullOrWhiteSpace($input)) {
        Write-Host 'Not a Yandex Music link. Example: https://music.yandex.ru/album/12345' -ForegroundColor Yellow
    }
}

& python "$Root\ym_download.py" "$url"
exit $LASTEXITCODE
