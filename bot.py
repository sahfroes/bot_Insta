import os
import logging
import re
import requests
from flask import Flask, request, jsonify
from dotenv import load_dotenv

from ia import gerar_resposta
from banco import (
    inicializar_banco, salvar_mensagem_historico, 
    buscar_historico, limpar_historico, consultar_cadastro
)

# 1. Configurações Iniciais
load_dotenv()

# Tokens obtidos no painel do Meta for Developers
ACCESS_TOKEN = os.getenv("INSTAGRAM_PAGE_ACCESS_TOKEN")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")  # Token de verificação 

app = Flask(__name__)

# Desativa logs repetitivos do Flask
hl = logging.getLogger('werkzeug')
hl.setLevel(logging.ERROR)

estado_usuarios = {} 

# ==========================================================
# 2. Funções de Comunicação com a API do Instagram
# ==========================================================

def enviar_mensagem_instagram(usuario_id, texto, quick_replies=None):
    """Envia texto e botões (Quick Replies) para o Direct do Instagram"""
    url = f"https://graph.facebook.com/v20.0/me/messages?access_token={ACCESS_TOKEN}"
    
    payload = {
        "recipient": {"id": usuario_id},
        "messaging_type": "RESPONSE",
        "message": {"text": texto}
    }
    
    # No Instagram, Quick Replies simula os botões de menu
    if quick_replies:
        payload["message"]["quick_replies"] = [
            {
                "content_type": "text",
                "title": botao["titulo"],
                "payload": botao["payload"]
            } for botao in quick_replies
        ]
        
    try:
        response = requests.post(url, json=payload)
        return response.json()
    except Exception as e:
        print(f"Erro ao enviar mensagem para o Instagram: {e}")

# ==========================================================
# 3. Menus e Fluxos de Conversa 
# ==========================================================

def exibir_menu_principal(usuario_id, nome="Doutor(a)"):
    texto = f"👋 Olá, {nome}!\n\nComo posso te ajudar hoje nos serviços do CFF?\n\nEscolha uma das opções nos botões abaixo:"
    botoes = [
        {"titulo": "🌐 Portal CFF", "payload": "MENU_SITE"},
        {"titulo": "🩺 Central Farmacêutico", "payload": "MENU_AJUDA"},
        {"titulo": "💬 Falar com a IA", "payload": "MENU_IA"},
        {"titulo": "🛠️ Suporte Técnico", "payload": "MENU_SUPORTE"}
    ]
    enviar_mensagem_instagram(usuario_id, texto, botoes)

def exibir_menu_farmaceutico(usuario_id):
    texto = "🩺 Central de Ajuda ao Farmacêutico\n\nComo os links diretos em botões funcionam diferente no Instagram, você pode acessar os portais digitando os links abaixo:\n\n📜 Legislação: site.cff.org.br/legislacao\n🪪 Cédula Digital: site.cff.org.br/cedula"
    botoes = [
        {"titulo": "« Voltar ao Menu", "payload": "MENU_VOLTAR"}
    ]
    enviar_mensagem_instagram(usuario_id, texto, botoes)

# ==========================================================
# 4. Lógica de Processamento de Mensagens
# ==========================================================

def processar_mensagem(usuario_id, texto_mensagem, payload_botao=None):
    # Se o usuário clicou em um botão (Quick Reply)
    payload = payload_botao or texto_mensagem.upper()

    # Comando de saída global
    if payload in ["SAIR", "/MENU", "MENU_VOLTAR"]:
        estado_usuarios.pop(usuario_id, None)
        limpar_historico(usuario_id)
        exibir_menu_principal(usuario_id)
        return

    # Se o usuário está na etapa de validação do CPF
    if estado_usuarios.get(usuario_id) == "AGUARDANDO_CPF":
        cpf_digitado = re.sub(r'\D', '', texto_mensagem)
        
        if len(cpf_digitado) != 11:
            enviar_mensagem_instagram(usuario_id, "⚠️ CPF inválido. Por favor, digite o CPF com 11 dígitos (apenas números):")
            return
            
        dados = consultar_cadastro(cpf_digitado)
        if dados:
            tratamento = "Doutora" if dados["genero"] == "F" else "Doutor"
            nome_completo = dados["nome"].split()[0]
            nome_final = f"{tratamento} {nome_completo}"
        else:
            nome_final = "Doutor(a) Visitante"
            
        estado_usuarios[usuario_id] = "LOGADO"
        enviar_mensagem_instagram(usuario_id, f"🎉 Cadastro verificado com sucesso, {nome_final}!")
        exibir_menu_principal(usuario_id, nome_final)
        return

    # Se o usuário está conversando com a IA
    if estado_usuarios.get(usuario_id) == "MODO_IA":
        salvar_mensagem_historico(usuario_id, role="user", content=texto_mensagem)
        historico = buscar_historico(usuario_id, limite=10)
        
        resposta_ia = gerar_resposta(historico, texto_mensagem)
        salvar_mensagem_historico(usuario_id, role="assistant", content=resposta_ia)
        
        botoes = [{"titulo": "« Sair da IA", "payload": "MENU_VOLTAR"}]
        enviar_mensagem_instagram(usuario_id, resposta_ia, botoes)
        return

    # Processamento dos botões principais
    if payload == "MENU_SITE":
        texto_site = "🌐 Portal do CFF\n\nAcesse o site oficial do Conselho Federal de Farmácia em:\n🔗 https://site.cff.org.br/"
        enviar_mensagem_instagram(usuario_id, texto_site, [{"titulo": "« Voltar", "payload": "MENU_VOLTAR"}])
        
    elif payload == "MENU_SUPORTE":
        texto_suporte = "🛠️ Suporte Técnico TI — CFF\n\n📧 E-mail: ti@cff.org.br\n🕒 Atendimento: Seg a Sex, 8h às 18h"
        enviar_mensagem_instagram(usuario_id, texto_suporte, [{"titulo": "« Voltar", "payload": "MENU_VOLTAR"}])
        
    elif payload == "MENU_AJUDA":
        exibir_menu_farmaceutico(usuario_id)
        
    elif payload == "MENU_IA":
        estado_usuarios[usuario_id] = "MODO_IA"
        limpar_historico(usuario_id)
        texto_ia = "💬 Modo Inteligente Ativado!\n\nEu sou a Samara. Pode me perguntar qualquer dúvida sobre o CFF que eu me lembrarei do contexto da nossa conversa.\n\n👉 Digite sua dúvida:"
        enviar_mensagem_instagram(usuario_id, texto_ia)
        
    else:
        # Se não está logado e mandou mensagem qualquer, pede CPF
        if estado_usuarios.get(usuario_id) is None:
            estado_usuarios[usuario_id] = "AGUARDANDO_CPF"
            texto_boas_vindas = "👋 Olá! Eu sou a Agente Samara, assistente virtual oficial do CFF.\n\nPara iniciar seu atendimento, por favor, digite seu CPF (apenas números):"
            enviar_mensagem_instagram(usuario_id, texto_boas_vindas)
        else:
            exibir_menu_principal(usuario_id)

# ==========================================================
# 5. Endpoints do Servidor Flask (O Webhook do Instagram)
# ==========================================================

@app.route('/webhook', methods=['GET'])
def verificar_webhook():
    """Validação necessária quando você configura o webhook no painel do Meta"""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode and token:
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            return challenge, 200
        return 'Token de verificação inválido', 403
    return 'Mecanismo Webhook CFF ativo', 200

@app.route('/webhook', methods=['POST'])
def receber_webhook():
    """Recebe as notificações em tempo real de mensagens enviadas no Instagram"""
    dados = request.get_json()
    
    try:
        if dados.get("object") == "instagram":
            for entrada in dados.get("entry", []):
                for evento_mensagem in entrada.get("messaging", []):
                    usuario_id = evento_mensagem["sender"]["id"]
                    
                    # Verifica se o usuário enviou texto ou clicou em um botão
                    if "message" in evento_mensagem:
                        msg_data = evento_mensagem["message"]
                        texto_mensagem = msg_data.get("text", "")
                        payload_botao = msg_data.get("quick_reply", {}).get("payload")
                        
                        # Ignora ecos (mensagens enviadas pelo próprio bot)
                        if "is_echo" not in msg_data:
                            processar_mensagem(usuario_id, texto_mensagem, payload_botao)
                            
    except Exception as e:
        print(f"Erro ao processar payload do webhook: {e}")
        
    return "EVENT_RECEIVED", 200

if __name__ == "__main__":
    print("Inicializando e verificando banco de dados...")
    inicializar_banco()
    
    port = int(os.environ.get("PORT", 10000))
    print(f"Servidor Webhook do Instagram rodando na porta {port}...")
    app.run(host='0.0.0.0', port=port)