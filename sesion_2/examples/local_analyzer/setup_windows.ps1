# ============================================================
# setup_windows.ps1 — Instalación Automática en Windows
# Fundamentos de Arquitectura LLM — Sesión 2, Tema 1
#
# Ejecutar como Administrador en PowerShell:
#   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#   .\examples\local_analyzer\setup_windows.ps1
#
# ============================================================

$ErrorActionPreference = "Stop"

function Write-Step { param([string]$msg) Write-Host "`n[*] $msg" -ForegroundColor Cyan }
function Write-OK   { param([string]$msg) Write-Host "    [OK] $msg" -ForegroundColor Green }
function Write-Warn { param([string]$msg) Write-Host "    [!!] $msg" -ForegroundColor Yellow }
function Write-Fail { param([string]$msg) Write-Host "    [XX] $msg" -ForegroundColor Red }

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  Fundamentos de Arquitectura LLM — Sesion 2" -ForegroundColor Cyan
Write-Host "  Instalacion automatica: Python + Ollama + API" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# ── Verificar privilegios de Administrador ─────────────────
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warn "Se recomienda ejecutar como Administrador para usar winget."
    Write-Warn "Continuando de todas formas..."
}

# ── Paso 1: Python 3.12 ────────────────────────────────────
Write-Step "Verificando Python 3.12..."
try {
    $pythonVersion = python --version 2>&1
    if ($pythonVersion -match "Python 3\.(1[2-9]|[2-9]\d)") {
        Write-OK "Python ya instalado: $pythonVersion"
    } else {
        Write-Warn "Python version inadecuada ($pythonVersion). Instalando 3.12..."
        winget install Python.Python.3.12 --silent
        Write-OK "Python 3.12 instalado"
    }
} catch {
    Write-Warn "Python no encontrado. Instalando..."
    winget install Python.Python.3.12 --silent
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine")
    Write-OK "Python 3.12 instalado"
}

# ── Paso 2: Ollama ─────────────────────────────────────────
Write-Step "Verificando Ollama..."
try {
    $ollamaVersion = ollama --version 2>&1
    Write-OK "Ollama ya instalado: $ollamaVersion"
} catch {
    Write-Warn "Ollama no encontrado. Instalando..."
    try {
        winget install Ollama.Ollama --silent
        Write-OK "Ollama instalado via winget"
    } catch {
        Write-Warn "winget fallo. Descargando manualmente..."
        $ollamaUrl = "https://ollama.ai/download/OllamaSetup.exe"
        $ollamaInstaller = "$env:TEMP\OllamaSetup.exe"
        Invoke-WebRequest -Uri $ollamaUrl -OutFile $ollamaInstaller
        Start-Process -FilePath $ollamaInstaller -Args "/S" -Wait
        Write-OK "Ollama instalado manualmente"
    }
    # Recargar PATH
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" +
                [System.Environment]::GetEnvironmentVariable("Path","User")
}

# ── Paso 3: Descargar modelo LLM ──────────────────────────
Write-Step "Descargando modelo Llama 3.2:3b (~2GB)..."
Write-Warn "Esto puede tardar 3-10 minutos segun tu conexion..."
try {
    # Iniciar Ollama si no esta corriendo
    $ollamaProcess = Get-Process -Name "ollama" -ErrorAction SilentlyContinue
    if (-not $ollamaProcess) {
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
        Write-OK "Ollama server iniciado en background"
    }
    
    ollama pull llama3.2:3b
    Write-OK "Modelo llama3.2:3b descargado"
} catch {
    Write-Fail "Error descargando modelo: $_"
    Write-Warn "Intentar manualmente: ollama pull llama3.2:3b"
}

# ── Paso 4: Entorno virtual Python ────────────────────────
Write-Step "Configurando entorno virtual Python..."
$venvPath = ".venv"

if (Test-Path $venvPath) {
    Write-OK "Entorno virtual ya existe en $venvPath"
} else {
    python -m venv $venvPath
    Write-OK "Entorno virtual creado en $venvPath"
}

# Activar entorno virtual
$activateScript = ".\$venvPath\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    & $activateScript
    Write-OK "Entorno virtual activado"
} else {
    Write-Fail "No se pudo activar el entorno virtual"
    exit 1
}

# ── Paso 5: Instalar dependencias ─────────────────────────
Write-Step "Instalando dependencias Python..."
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
Write-OK "Dependencias instaladas"

# ── Paso 6: Variables de entorno ──────────────────────────
Write-Step "Configurando variables de entorno..."
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-OK "Archivo .env creado desde .env.example"
    Write-Warn "El .env ya esta configurado para uso local (Tema 1)"
    Write-Warn "Para Azure (Tema 2), editar: AZURE_AI_ENDPOINT y AZURE_AI_KEY"
} else {
    Write-OK "Archivo .env ya existe"
}

# ── Paso 7: Verificacion final ────────────────────────────
Write-Step "Verificacion del sistema..."

# Verificar Ollama
try {
    $models = ollama list 2>&1
    Write-OK "Ollama responde correctamente"
    Write-OK "Modelos disponibles:`n$models"
} catch {
    Write-Warn "Ollama no responde. Ejecutar manualmente: ollama serve"
}

# ── Resultado ──────────────────────────────────────────────
Write-Host "`n================================================" -ForegroundColor Green
Write-Host "  INSTALACION COMPLETADA" -ForegroundColor Green
Write-Host "================================================" -ForegroundColor Green
Write-Host ""
Write-Host "PASOS SIGUIENTES:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Activar el entorno virtual (si no esta activo):" -ForegroundColor White
Write-Host "   .\.venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Iniciar la API local (Tema 1):" -ForegroundColor White
Write-Host "   make run-local" -ForegroundColor Gray
Write-Host "   # O directamente:" -ForegroundColor DarkGray
Write-Host "   uvicorn examples.local_analyzer.main:app --port 8001 --reload" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Abrir Swagger UI en el browser:" -ForegroundColor White
Write-Host "   http://localhost:8001/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "4. Ejecutar demo rapido:" -ForegroundColor White
Write-Host "   curl http://localhost:8001/credit/demo" -ForegroundColor Gray
Write-Host ""
Write-Host "Para el Tema 2 (Azure), editar el archivo .env con tus credenciales." -ForegroundColor Yellow
Write-Host ""
