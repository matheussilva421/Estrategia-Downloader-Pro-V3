# 🦉 Estratégia Downloader Pro v3.2

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-3.2-green.svg)](https://github.com/seu-usuario/estrategia-downloader-pro)

Downloader automatizado, seguro e profissional para cursos da plataforma Estratégia Concursos.

## ✨ O que há de novo na v3.2?

Esta versão traz correções críticas de estabilidade e melhorias de performance:
- 🛡️ **Race conditions corrigidas**: Barra de progresso sempre precisa.
- 💾 **Gestão de Log**: Rotação automática para evitar arquivos gigantes.
- 🧹 **Limpeza Automática**: Interface mais leve removendo downloads concluídos.
- ✅ **Validação Extra**: Proteção contra arquivos HTML sendo salvos como PDF/MP4.

### Principais Recursos
- **Vídeos em Alta Definição** (até 1080p se disponível)
- **Materiais Complementares** (Mapas Mentais, Resumos, Slides)
- **PDFs das Aulas** (Simplificado, Original, Marcado)
- **Criptografia de Senhas** (AES-128 via Fernet)
- **Interface Moderna** (Dark Mode)

## 📋 Sumário

- [Instalação](#-instalação)
- [Como Usar](#-como-usar)
- [Materiais Complementares](#-materiais-complementares)
- [Estrutura de Pastas](#-estrutura-de-pastas)
- [Configurações](#-configurações)
- [Troubleshooting](#-troubleshooting)

## 🔧 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- Google Chrome instalado
- Windows 10/11 (compatível com Linux/Mac)

### 1. Preparação
```bash
# Extraia o arquivo zip
unzip estrategia-downloader-pro-v3.2.zip
cd estrategia-downloader-pro-v3.2
```

### 2. Instalação
```bash
# Instale dependências
pip install -r requirements.txt

# Instale navegador
playwright install chromium
```

## 🚀 Como Usar

### Interface Gráfica (Recomendado)
Execute:
```bash
python app.py
```

1. **Login**: Na aba Configurações, insira email e senha (serão criptografados).
2. **URLs**: Na aba Cursos, cole a URL da página de aulas.
   - Ex: `https://www.estrategiaconcursos.com.br/app/dashboard/cursos/123456/aulas`
3. **Iniciar**: Volte para a aba Início e clique em "INICIAR DOWNLOADS".

### Linha de Comando (Headless)
Execute:
```bash
python downloader.py
```

## 🎁 Materiais Complementares

O programa detecta e baixa automaticamente os materiais extras associados aos vídeos:
- 🗺️ **Mapas Mentais**
- 📝 **Resumos**
- 📊 **Slides**

### Como Ativar
Vá em **Configurações > Vídeo** e marque a opção **"Baixar Materiais Extras"**.

### Estrutura de Pastas
Os arquivos são organizados automaticamente por aula e tipo:

```
Estrategia_Videos/
└── Auditoria Governamental/
    ├── Aula 01 - Introdução/
    │   ├── Vídeo - Planejamento [720p].mp4
    │   ├── Vídeo - Planejamento - Mapa Mental.pdf  
    │   ├── Vídeo - Planejamento - Resumo.pdf      
    │   └── Vídeo - Planejamento - Slides.pdf
    └── ...
```

## ⚙️ Configurações

### Arquivo `config.json`
Criado automaticamente na primeira execução. Você pode editar manualmente:

```json
{
  "email": "seu@email.com",
  "downloadType": "video",
  "videoConfig": {
    "pastaDownloads": "C:\\Downloads\\Videos",
    "resolucaoEscolhida": "720p",
    "baixarExtras": true
  },
  "pdfConfig": {
    "pastaDownloads": "C:\\Downloads\\PDFs",
    "pdfType": 2,
    "baixarMateriaisDeVideo": false
  }
}
```

## ❓ Troubleshooting

### O download trava ou não inicia?
- Verifique sua conexão.
- Limpe o arquivo `downloader.log` se necessário (agora é automático!).
- Certifique-se de que não há janelas do Chrome bloqueando o processo.

### "Erro ao logar"?
- Verifique email e senha.
- Se mudou a senha no site, atualize nas configurações.

### Log Gigante?
- A versão v3.2 corrige isso automaticamente rotacionando os logs a cada 5MB.


---
**Aviso Legal**: Este software é para uso pessoal e educacional. Não distribua materiais protegidos por direitos autorais.
|-------|---------|--------|-----------|
| **Pasta de Vídeos** | Caminho | `~/Downloads/Estrategia_Videos` | Onde salvar |
| **Resolução** | `720p`, `480p`, `360p` | `720p` | Qualidade |
| **✨ Baixar Extras** | `true`, `false` | `true` | Mapas/Resumos/Slides |

### Configurações de PDF

| Opção | Valores | Padrão | Descrição |
|-------|---------|--------|-----------|
| **Pasta de PDFs** | Caminho | `~/Downloads/Estrategia_PDFs` | Onde salvar |
| **Tipo de PDF** | `1`, `2`, `3`, `4` | `2` | Qual versão |

**Tipos de PDF:**
- `1` - Versão Simplificada
- `2` - Versão Original (recomendado)
- `3` - Marcação dos Aprovados
- `4` - Todos os tipos

## 📊 Comparação de Versões

| Recurso | v2.0 | v2.1 | v3.2 (Atual) |
|---------|------|------|--------------|
| Download de PDFs | ✅ | ✅ | ✅ |
| Download de Vídeos | ✅ | ✅ | ✅ |
| **Mapas Mentais/Resumos** | ❌ | ✅ | ✅ |
| Senha Criptografada | ✅ | ✅ | ✅ |
| **Estabilidade (Anti-Crash)** | ❌ | ❌ | ✅ |
| **Log Otimizado (Rotação)** | ❌ | ❌ | ✅ |
| **Correção Memory Leak** | ❌ | ❌ | ✅ |

## ❓ Perguntas Frequentes

### P: Os materiais extras aumentam muito o tempo de download?

**R:** Sim, em cerca de 40%. Exemplo:
- Apenas vídeos: ~5 min por curso
- Vídeos + extras: ~7-10 min por curso

Mas **vale muito a pena** ter todo o material organizado!

### P: Posso baixar apenas os extras sem os vídeos?

**R:** Não diretamente. Mas você pode:
1. Baixar tudo
2. Deletar os arquivos `.mp4`
3. Manter apenas os PDFs

### P: E se um vídeo não tiver mapa mental?

**R:** Normal! O sistema detecta automaticamente e pula sem erro:
```
ℹ️  Sem mapa mental para 'Vídeo X'
ℹ️  Sem resumo para 'Vídeo X'
```

### P: Os extras consomem muito espaço em disco?

**R:** PDFs são pequenos. Geralmente 20-30% a mais que apenas vídeos.

