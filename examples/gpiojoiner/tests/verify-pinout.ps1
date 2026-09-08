$ErrorActionPreference = 'Stop'
$pagePath = Join-Path $PSScriptRoot '..\index.html'
if (-not (Test-Path $pagePath)) { throw 'index.html does not exist' }
$html = Get-Content -Raw $pagePath

$required = @(
  '<!doctype html>', 'id="pinout"', 'id="legend"', 'id="details"',
  'aria-live="polite"', 'data-action="reset"', 'const pinData =',
  'renderPinout()', 'selectPin(', 'selectGroup(', 'resetSelection()',
  'Breakout group', 'data-variant-groups', 'matching-variant', 'layout-test-result',
  'desktop-layout-test-result'
)
foreach ($text in $required) {
  if (-not $html.Contains($text)) { throw "Missing required page content: $text" }
}

$pinObjects = [regex]::Matches($html, '(?m)^\s*\{ pin: (\d+), variants:')
if ($pinObjects.Count -ne 20) { throw "Expected 20 pin objects; found $($pinObjects.Count)" }
$pins = @($pinObjects | ForEach-Object { [int]$_.Groups[1].Value } | Sort-Object)
if ((Compare-Object $pins @(1..20)).Count) { throw 'Pin data must contain pins 1 through 20 exactly once' }

$expectedData = @(
  '1|spi|Both^SPI1_CS_OUT^GPIO13^Output^spi^SPI^spi','2|power|Both^5V OUT^-^Power output^power^Power^power','3|gpio|Both^GPIO_27_OUT^GPIO27^Output^gpio^GPIO^gpio',
  '4|vref power|OG^VREF^-^Power input^vref^VREF^vref power;FW2^TRIG IN/VREF^-^Input^vref^VREF^vref power','5|uart|Both^UART1_Rx_IN^GPIO9^Input^uart^UART^uart',
  '6|power|Both^3.3V OUT^-^Power output^power^Power^power','7|uart|Both^UART1_CTS_IN^GPIO10^Input^uart^UART^uart','8|i2c|Both^I2C 0 SCL^GPIO17^Bidirectional^i2c^I2C^i2c',
  '9|uart|Both^UART1_Tx_OUT^GPIO8^Output^uart^UART^uart','10|i2c|Both^I2C 0 SDA^GPIO16^Bidirectional^i2c^I2C^i2c','11|uart|Both^UART1_RTS_OUT^GPIO11^Output^uart^UART^uart',
  '12|spi|Both^SPI1_Rx_IN^GPIO12^Input^spi^SPI^spi','13|spi|Both^SPI1_Tx_OUT^GPIO15^Output^spi^SPI^spi','14|gpio|Both^GPIO26_IN_BI^GPIO26^Input^gpio^GPIO^gpio',
  '15|spi|Both^SPI1_SCLK_OUT^GPIO14^Output^spi^SPI^spi','16|debug canfd|OG^SWCLK IN^SWCLK^Input^debug^Debug^debug;FW2^CANFD L^-^Bidirectional^canfd^CANFD^canfd',
  '17|gpio|Both^GPIO25_OUT^GPIO25^Output^gpio^GPIO^gpio','18|debug canfd|OG^SWDIO^SWDIO^Bidirectional^debug^Debug^debug;FW2^CANFD H^-^Bidirectional^canfd^CANFD^canfd',
  '19|ground|Both^GND^-^Ground^ground^Ground^ground','20|ground|Both^GND^-^Ground^ground^Ground^ground'
)
foreach ($expectedPin in $expectedData) {
  $dataFields = $expectedPin -split '\|', 3
  $pin = [int]$dataFields[0]
  $object = [regex]::Match($html, "(?s)\{ pin: $pin, variants: \[(?<variants>.*?)\], groups: \[(?<groups>.*?)\] \}")
  if (-not $object.Success) { throw "Missing bounded data object for pin $pin" }
  $expectedGroups = ($dataFields[1] -split ' ' | ForEach-Object { "'$_'" }) -join ', '
  if ($object.Groups['groups'].Value -ne $expectedGroups) { throw "Pin $pin groups do not match authoritative data" }
  $variantIndex = 0
  foreach ($expectedVariant in ($dataFields[2] -split ';')) {
    $variantFields = $expectedVariant -split '\^'
    $expectedText = "device: '$($variantFields[0])', signal: '$($variantFields[1])', gpio: '$($variantFields[2])', direction: '$($variantFields[3])', color: '$($variantFields[4])', breakout: '$($variantFields[5])', groups: '$($variantFields[6])'"
    $actualIndex = $object.Groups['variants'].Value.IndexOf($expectedText)
    if ($actualIndex -lt 0) { throw "Pin $pin is missing authoritative variant: $expectedText" }
    if ($actualIndex -lt $variantIndex) { throw "Pin $pin variants are not in authoritative order" }
    $variantIndex = $actualIndex
  }
}

if ($html -match '<script\s+src=|<link[^>]+stylesheet|https?://[^\s"'']+\.(js|css)') {
  throw 'Page must not depend on external JavaScript or stylesheets'
}

$edgePath = 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
if (-not (Test-Path $edgePath)) { throw "Microsoft Edge is required for the direct-file interaction smoke test: $edgePath" }
$pageUrl = 'file:///' + (($pagePath -replace '\\', '/') + '#self-test=1')
$domPath = Join-Path ([IO.Path]::GetTempPath()) 'free-wili-interaction-smoke-dom.html'
$errorPath = Join-Path ([IO.Path]::GetTempPath()) 'free-wili-interaction-smoke-error.txt'
$edgeProcess = Start-Process -FilePath $edgePath -ArgumentList @('--headless=new', '--disable-gpu', '--no-first-run', '--dump-dom', $pageUrl) -NoNewWindow -PassThru -Wait -RedirectStandardOutput $domPath -RedirectStandardError $errorPath
if ($edgeProcess.ExitCode -ne 0) { throw "Edge direct-file interaction smoke test failed to run (exit $($edgeProcess.ExitCode))" }
$renderedDomText = Get-Content -Raw $domPath
Remove-Item -LiteralPath $domPath
Remove-Item -LiteralPath $errorPath
if ($renderedDomText -notmatch 'id="interaction-test-result" data-status="pass"') {
  throw 'Direct-file interaction smoke test did not report pass'
}

$layoutDomPath = Join-Path ([IO.Path]::GetTempPath()) 'free-wili-layout-smoke-dom.html'
$layoutErrorPath = Join-Path ([IO.Path]::GetTempPath()) 'free-wili-layout-smoke-error.txt'
$layoutUrl = 'file:///' + (($pagePath -replace '\\', '/') + '#layout-test=1')
$layoutProcess = Start-Process -FilePath $edgePath -ArgumentList @('--headless=new', '--disable-gpu', '--no-first-run', '--window-size=375,900', '--dump-dom', $layoutUrl) -NoNewWindow -PassThru -Wait -RedirectStandardOutput $layoutDomPath -RedirectStandardError $layoutErrorPath
if ($layoutProcess.ExitCode -ne 0) { throw "Edge 375px layout smoke test failed to run (exit $($layoutProcess.ExitCode))" }
$layoutDomText = Get-Content -Raw $layoutDomPath
Remove-Item -LiteralPath $layoutDomPath
Remove-Item -LiteralPath $layoutErrorPath
if ($layoutDomText -notmatch 'id="layout-test-result" data-status="pass"') {
  throw 'Edge 375px layout smoke test did not report pass'
}

$desktopDomPath = Join-Path ([IO.Path]::GetTempPath()) 'free-wili-desktop-layout-smoke-dom.html'
$desktopErrorPath = Join-Path ([IO.Path]::GetTempPath()) 'free-wili-desktop-layout-smoke-error.txt'
$desktopUrl = 'file:///' + (($pagePath -replace '\\', '/') + '#desktop-layout-test=1')
$desktopProcess = Start-Process -FilePath $edgePath -ArgumentList @('--headless=new', '--disable-gpu', '--no-first-run', '--window-size=1440,1000', '--dump-dom', $desktopUrl) -NoNewWindow -PassThru -Wait -RedirectStandardOutput $desktopDomPath -RedirectStandardError $desktopErrorPath
if ($desktopProcess.ExitCode -ne 0) { throw "Edge desktop layout smoke test failed to run (exit $($desktopProcess.ExitCode))" }
$desktopDomText = Get-Content -Raw $desktopDomPath
Remove-Item -LiteralPath $desktopDomPath
Remove-Item -LiteralPath $desktopErrorPath
if ($desktopDomText -notmatch 'id="desktop-layout-test-result" data-status="pass"') {
  throw 'Edge desktop layout smoke test did not report pass'
}

'PASS: authoritative 20-pin data, all categories, differing variants, interactions, 375px layout, and full-width desktop layout verified'
