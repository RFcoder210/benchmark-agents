# ============================================================================
# iniciar-sessao.ps1 — Carrega SOMENTE o contexto de retomada (hook)
# ----------------------------------------------------------------------------
# Quando roda: ao abrir o Claude Code, ao retomar uma conversa, após /clear
# e após uma compactação de contexto.
#
# O que faz:
#   Entrega ao Claude a data de hoje e o conteúdo de .plano/RETOMADA.md.
#   Nada além disso: o histórico antigo NÃO é carregado. É o "bilhete na
#   geladeira" do turno anterior — curto e suficiente para continuar.
# ============================================================================

# UTF-8 sem BOM: evita acentos quebrados e caracteres invisíveis na saída
$utf8SemBom = New-Object System.Text.UTF8Encoding $false
[Console]::InputEncoding  = $utf8SemBom
[Console]::OutputEncoding = $utf8SemBom

$LIMITE_CARACTERES = 7000   # o Claude Code aceita até 10.000 por hook

try { $entrada = [Console]::In.ReadToEnd() | ConvertFrom-Json } catch { $entrada = $null }

$raiz = $env:CLAUDE_PROJECT_DIR
if (-not $raiz -and $entrada) { $raiz = $entrada.cwd }
if (-not $raiz) { exit 0 }

$origem = ''
if ($entrada) { $origem = [string]$entrada.source }

$ptBR = [System.Globalization.CultureInfo]::GetCultureInfo('pt-BR')
$agora = Get-Date
$linhas = @()
$linhas += ("Data atual: {0} ({1}), {2}." -f $agora.ToString('yyyy-MM-dd'), $agora.ToString('dddd', $ptBR), $agora.ToString('HH:mm'))

# Neste projeto (benchmark) não usamos a orquestração do CRM: o estado
# duradouro fica na seção "Estado atual" do CLAUDE.md e o bilhete do dia
# em .plano/RETOMADA.md, gravado pela skill /encerrar-dia.
$pastaPlano  = Join-Path $raiz '.plano'
$arqRetomada = Join-Path $pastaPlano 'RETOMADA.md'

if ($origem -eq 'compact') {
    $linhas += "A conversa acabou de ser compactada. O estado duradouro do projeto está na seção 'Estado atual' do CLAUDE.md."
}

if (Test-Path $arqRetomada) {
    $texto = Get-Content -Raw -Encoding UTF8 $arqRetomada
    if (-not $texto) { $texto = '(arquivo vazio)' }
    if ($texto.Length -gt $LIMITE_CARACTERES) {
        $texto = $texto.Substring(0, $LIMITE_CARACTERES) + "`n[... RETOMADA.md truncado; ler o arquivo completo se necessário ...]"
    }
    $linhas += "Contexto de retomada do projeto (conteúdo de .plano/RETOMADA.md):"
    $linhas += "-----"
    $linhas += $texto.Trim()
    $linhas += "-----"
} else {
    $linhas += "Não há .plano/RETOMADA.md; o estado do projeto está na seção 'Estado atual' do CLAUDE.md."
}

# Última medição de uso, se houver
$arqUso = Join-Path $pastaPlano 'estado/uso.json'
if (Test-Path $arqUso) {
    try {
        $uso = Get-Content -Raw -Encoding UTF8 $arqUso | ConvertFrom-Json
        $quando = [string]$uso.atualizado_em
        try { $quando = ([datetime]$uso.atualizado_em).ToString('dd/MM HH:mm') } catch { }
        $p5 = 'n/d'; if ($null -ne $uso.janela_5h_pct) { $p5 = "$($uso.janela_5h_pct)%" }
        $pS = 'n/d'; if ($null -ne $uso.semanal_pct) { $pS = "$($uso.semanal_pct)%" }
        $linhas += ("Última medição de uso registrada ({0}): janela 5h {1}, semana {2}." -f $quando, $p5, $pS)
    } catch { }
}

# Nome da sessão: "Dia N · DD/MM · foco". N vem da última linha de .plano/DIARIO.md:
# se a data de hoje já está lá, é o mesmo dia; senão, é o próximo número.
$arqDiario = Join-Path $pastaPlano 'DIARIO.md'
$hoje = $agora.ToString('yyyy-MM-dd')
$numeroDia = 1
$jaRegistrado = $false
if (Test-Path $arqDiario) {
    $linhasDiario = Get-Content -Encoding UTF8 $arqDiario | Where-Object { $_ -match '^\|\s*\d+\s*\|' }
    if ($linhasDiario) {
        $ultima = @($linhasDiario)[-1]
        $partes = $ultima.Split('|')
        $ultimoN = [int]$partes[1].Trim()
        $jaRegistrado = ($partes[2].Trim() -eq $hoje)
        $numeroDia = if ($jaRegistrado) { $ultimoN } else { $ultimoN + 1 }
    }
}
$sufixo = if ($jaRegistrado) { ' (2)' } else { '' }
$linhas += ("Nome da sessão: se o título atual não segue o padrão, renomeie-a logo no início com set_session_title (session_id 'self') para 'Dia {0} · {1} · <foco em 2 a 5 palavras>{2}', com o foco tirado da 'Próxima ação'. Se for um dia novo, acrescente a linha do Dia {0} em .plano/DIARIO.md." -f $numeroDia, $agora.ToString('dd/MM'), $sufixo)
$linhas += "Rotina: uma sessão por dia. Comece pela 'Próxima ação' da retomada; ao terminar o dia, o usuário digita /encerrar-dia."
Write-Output ($linhas -join "`n")
exit 0
