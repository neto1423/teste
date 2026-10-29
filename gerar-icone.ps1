Add-Type -AssemblyName System.Drawing

$size = 256
$bitmap = New-Object System.Drawing.Bitmap($size, $size, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.Clear([System.Drawing.Color]::Transparent)

$bounds = New-Object System.Drawing.Rectangle(8, 8, 240, 240)
$backgroundPath = New-Object System.Drawing.Drawing2D.GraphicsPath
$backgroundPath.AddArc(8, 8, 64, 64, 180, 90)
$backgroundPath.AddArc(184, 8, 64, 64, 270, 90)
$backgroundPath.AddArc(184, 184, 64, 64, 0, 90)
$backgroundPath.AddArc(8, 184, 64, 64, 90, 90)
$backgroundPath.CloseFigure()
$gradient = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
    $bounds,
    [System.Drawing.Color]::FromArgb(255, 246, 77, 96),
    [System.Drawing.Color]::FromArgb(255, 111, 45, 165),
    45
)
$graphics.FillPath($gradient, $backgroundPath)

$pen = New-Object System.Drawing.Pen([System.Drawing.Color]::White, 14)
$pen.StartCap = [System.Drawing.Drawing2D.LineCap]::Round
$pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
$cameraPath = New-Object System.Drawing.Drawing2D.GraphicsPath
$cameraPath.AddArc(55, 55, 44, 44, 180, 90)
$cameraPath.AddArc(157, 55, 44, 44, 270, 90)
$cameraPath.AddArc(157, 157, 44, 44, 0, 90)
$cameraPath.AddArc(55, 157, 44, 44, 90, 90)
$cameraPath.CloseFigure()
$graphics.DrawPath($pen, $cameraPath)
$graphics.DrawEllipse($pen, 88, 88, 80, 80)
$graphics.FillEllipse([System.Drawing.Brushes]::White, 164, 76, 17, 17)

$iconPath = Join-Path $PSScriptRoot 'instagram-style.ico'
$handle = $bitmap.GetHicon()
$icon = [System.Drawing.Icon]::FromHandle($handle)
$stream = [System.IO.File]::Create($iconPath)
$icon.Save($stream)
$stream.Dispose()
$icon.Dispose()
$graphics.Dispose()
$bitmap.Dispose()
$gradient.Dispose()
$pen.Dispose()
$backgroundPath.Dispose()
$cameraPath.Dispose()
Write-Output $iconPath
