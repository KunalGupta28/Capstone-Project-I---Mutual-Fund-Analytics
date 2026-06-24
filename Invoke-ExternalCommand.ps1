# Robust PowerShell execution wrapper to bypass hosted runspace command pipeline bug

function Invoke-ExternalCommand {
    param (
        [Parameter(Mandatory=$true)]
        [string]$FileName,
        [string]$Arguments = "",
        [string]$WorkingDirectory = "c:\Users\Dell\Desktop\Internship_coding"
    )
    
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $FileName
    $psi.Arguments = $Arguments
    $psi.WorkingDirectory = $WorkingDirectory
    $psi.UseShellExecute = $false
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    
    $p = New-Object System.Diagnostics.Process
    $p.StartInfo = $psi
    
    # Thread-safe queues to collect stdout and stderr
    $queue = New-Object System.Collections.Concurrent.ConcurrentQueue[string]
    $errQueue = New-Object System.Collections.Concurrent.ConcurrentQueue[string]
    
    # Register events using MessageData to safely pass queue references across runspace thread boundaries
    $outEvent = Register-ObjectEvent -InputObject $p -EventName "OutputDataReceived" -Action {
        if ($EventArgs.Data -ne $null) {
            $Event.MessageData.Enqueue($EventArgs.Data)
        }
    } -MessageData $queue
    
    $errEvent = Register-ObjectEvent -InputObject $p -EventName "ErrorDataReceived" -Action {
        if ($EventArgs.Data -ne $null) {
            $Event.MessageData.Enqueue($EventArgs.Data)
        }
    } -MessageData $errQueue
    
    try {
        $started = $p.Start()
        if (-not $started) {
            throw "Failed to start process: $FileName"
        }
        
        $p.BeginOutputReadLine()
        $p.BeginErrorReadLine()
        
        # Read queues while process is active
        while (-not $p.HasExited) {
            $line = $null
            while ($queue.TryDequeue([ref]$line)) {
                Write-Host $line
            }
            $errLine = $null
            while ($errQueue.TryDequeue([ref]$errLine)) {
                Write-Error $errLine
            }
            Start-Sleep -Milliseconds 50
        }
        
        # Flush remaining output after exit
        Start-Sleep -Milliseconds 100
        $line = $null
        while ($queue.TryDequeue([ref]$line)) { Write-Host $line }
        $errLine = $null
        while ($errQueue.TryDequeue([ref]$errLine)) { Write-Error $errLine }
        
        # Clean up events
        Unregister-Event -SourceIdentifier $outEvent.Name -ErrorAction SilentlyContinue
        Unregister-Event -SourceIdentifier $errEvent.Name -ErrorAction SilentlyContinue
        
        $exitCode = $p.ExitCode
        if ($exitCode -ne 0) {
            throw "Command '$FileName $Arguments' failed with exit code $exitCode"
        }
        return $exitCode
    } catch {
        if ($outEvent) { Unregister-Event -SourceIdentifier $outEvent.Name -ErrorAction SilentlyContinue }
        if ($errEvent) { Unregister-Event -SourceIdentifier $errEvent.Name -ErrorAction SilentlyContinue }
        throw $_
    } finally {
        $p.Dispose()
    }
}

function Invoke-Python {
    param([string]$ArgsList)
    Invoke-ExternalCommand -FileName "python.exe" -Arguments $ArgsList
}

function Invoke-Git {
    param([string]$ArgsList)
    Invoke-ExternalCommand -FileName "git.exe" -Arguments $ArgsList
}

function Invoke-Node {
    param([string]$ArgsList)
    Invoke-ExternalCommand -FileName "node.exe" -Arguments $ArgsList
}

function Invoke-Npm {
    param([string]$ArgsList)
    Invoke-ExternalCommand -FileName "npm.cmd" -Arguments $ArgsList
}
