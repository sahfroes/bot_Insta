```markdown
# 🩺 Agente Samara — Assistente Virtual CFF

A **Agente Samara** é um bot automatizado para o Telegram integrado a um servidor de monitoramento Flask. Ela foi desenvolvida para otimizar a rotina e centralizar o acesso a serviços essenciais para farmacêuticos e profissionais no ecossistema do **Conselho Federal de Farmácia (CFF)**.

---

## 🚀 Funcionalidades Atuais

- **Menu Dinâmico Inline:** Navegação limpa e intuitiva usando botões clicáveis (`edit_message_text`) que atualizam o chat de forma fluida sem poluir o histórico de mensagens.
- **Central do Farmacêutico:** Atalhos diretos e seguros para serviços de alta demanda, como Emissão de Cédula Digital, Consulta de Legislação, Manuais Práticos e acesso ao Sistema SEI.
- **Suporte Técnico Integrado:** Acesso rápido às informações de contato (e-mail, telefone e horários) da equipe de TI do CFF.
- **Escuta Inteligente (Fricção Zero):** O bot possui tratamento de resiliência que responde perfeitamente a saudações comuns (como "Oi" ou "Menu"), cliques perdidos ou erros típicos de digitação (ex: `\start`), garantindo suporte imediato.
- **Servidor de Sobrevivência (Keep-Alive):** Integração com Flask e threads assíncronas para garantir atividade contínua 24/7, respondendo a pings externos para evitar suspensão em ambientes de nuvem.

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.14+**
- **Flask:** Micro-framework web utilizado para expor a porta de monitoramento.
- **Python-dotenv:** Gerenciamento seguro de credenciais e variáveis de ambiente.

---

## 📂 Estrutura do Projeto

```text
bot_Samara/
├── banco.py           # Código-fonte para este com banco de dados com nomes e cpfs ficticios
├── bot.py             # Código-fonte principal do bot e servidor Flask
├── .env               # Variáveis de ambiente confidenciais (Ignorado no Git)
├── ia.py              # Código-fonte para gerar respostas  
└── README.md          # Documentação do projeto
```

---

## 📦 Como Rodar o Projeto Localmente

### 1. Clonar o Repositório
```bash
git clone https://github.com/sahfroes/bot_Insta.git
cd bot_insta
```

### 2. Instalar as Dependências
Certifique-se de ter o Python instalado e execute o comando abaixo para instalar as bibliotecas necessárias:
```bash
pip install  python-dotenv flask
```

### 3. Configurar as Variáveis de Ambiente
Crie um arquivo chamado `.env` exatamente na raiz do projeto e insira a chave obtida do instagram com o facebook
```env
CHAVE_API=SEU_TOKEN
```
> ⚠️ **Atenção:** Nunca envie o arquivo `.env` para o seu repositório público do GitHub para manter o token do seu bot protegido.

### 4. Executar a Aplicação
```bash
python bot.py
```

---

## 🌐 Deploy (Hospedagem no Render)

Este projeto foi desenhado para funcionar perfeitamente na nuvem do **Render** (Web Service). A arquitetura utiliza a função `keep_alive()` para manter o serviço ativo mesmo nas camadas gratuitas da plataforma.

Para realizar a implantação, utilize as seguintes configurações no painel do Render:

- **Environment:** `Python`
- **Build Command:** `pip install  python-dotenv flask`
- **Start Command:** `python bot.py`
- **Advanced > Environment Variables:** Adicione a chave `CHAVE_API` com o seu token do Telegram.

---

## 👤 Autora

Desenvolvido por **Sarah Fróes**.
```