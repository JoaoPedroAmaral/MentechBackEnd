from flask import jsonify
from Database.database import conectar_base_de_dados
from Controller.mensagens import enviar_mensagem_negativa, enviar_mensagem_positiva
from Controller.log import registrar_log_alterar_senha
from Database.database import load_dotenv
import smtplib
import secrets
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

load_dotenv()
senha = os.getenv("CRIPT_PASSWORD")
email = os.getenv("EMAIL_USER")
emailSenha = os.getenv("EMAIL_PASSWORD")

def carregar_pedidos():
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    cursor.execute("SELECT cd_alterar_senha, cd_usuario, email, CAST(AES_DECRYPT(token, %s) AS CHAR) AS token, utilizado, CAST(ti_validade AS CHAR) AS ti_validade, CAST(timestamp AS CHAR) AS timestamp FROM alterar_senha", (senha,))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def carregar_pedidos_por_id_usuario(cd_usuario):
    bd = conectar_base_de_dados()
    cursor = bd.cursor(dictionary=True)
    # ✅ CORRIGIDO: Adicionada vírgula antes do parênteses
    cursor.execute("SELECT cd_alterar_senha, cd_usuario, email, CAST(AES_DECRYPT(token, %s) AS CHAR) AS token, utilizado, CAST(ti_validade AS CHAR) AS ti_validade, CAST(timestamp AS CHAR) AS timestamp FROM alterar_senha WHERE cd_usuario = %s", (senha, cd_usuario))
    linhas = cursor.fetchall()
    bd.close()
    return linhas

def criar_solicitacao(cd_usuario, email_destino):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()

    try:
        # 1️⃣ Gerar token aleatório seguro
        token = secrets.token_urlsafe(32)

        # 2️⃣ Inserir na tabela
        sql = """INSERT INTO alterar_senha (cd_usuario, email, token, utilizado)
                 VALUES (%s, %s, AES_ENCRYPT(%s, %s), 'N')"""
        cursor.execute(sql, (cd_usuario, email_destino, token, senha))
        bd.commit()
        id_solicitacao = cursor.lastrowid
        
        # registra log
        # registrar_log_alterar_senha(tipo_log='SAS', cd_usuario=cd_usuario) 

        # 3️⃣ Gerar link de redefinição
        link = f"http://mentech.app.br/redefinir-senha/{id_solicitacao}/{cd_usuario}/{token}"

        # 4️⃣ Enviar o e-mail
        enviar_email_recuperacao(email_destino, link)

        return jsonify({
            "MSG224": enviar_mensagem_positiva("MSG224"),
            "cd_alterar_senha": id_solicitacao
        }), 201

    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao criar solicitação: {e}"}), 400
    finally:
        bd.close()

def enviar_email_recuperacao(destinatario, link):
    remetente = email
    senha_email = emailSenha 

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Recuperação de senha - MenTech"
    msg["From"] = remetente
    msg["To"] = destinatario

    corpo_html = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background: #4EA2A9; padding: 40px; margin: 0;">
        <div style="background: #F5F5F5; border-radius: 15px; padding: 30px; max-width: 600px; margin: auto; box-shadow: 0 4px 15px rgba(0,0,0,0.1); text-align: center;">

        <img src="https://img.icons8.com/ios-filled/50/4EA2A9/key.png" alt="Key Icon" style="margin-bottom: 20px; width: 50px; height: 50px;"/>
        
        <h2 style="color: #4EA2A9; margin-bottom: 20px;">Recuperação de senha</h2>
        
        <p style="color: #333; font-size: 16px; line-height: 1.5;">
            Você solicitou a redefinição de senha. Clique no botão abaixo para criar uma nova:
        </p>
        
        <a href="{link}" 
            style="display: inline-block; background: #B39DDB; color: white; 
                    text-decoration: none; padding: 12px 25px; border-radius: 8px;
                    font-weight: bold; font-size: 16px; margin: 20px 0; transition: background 0.3s; cursor: pointer;">
            Renovar senha
        </a>
        
        <p style="color: #777; font-size: 12px; margin-top: 20px;">
            Se você não fez esta solicitação, ignore este e-mail.
        </p>
        
        <p style="color: #999; font-size: 11px; margin-top: 30px; border-top: 1px solid #ddd; padding-top: 15px;">
            Este link expira em 24 horas por motivos de segurança.
        </p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(corpo_html, "html"))

    try:
        # ✅ Usando SMTP_SSL na porta 465 (método mais seguro)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(remetente, senha_email)
            server.sendmail(remetente, destinatario, msg.as_string())
        print(f"✅ E-mail enviado com sucesso para {destinatario}")
    except Exception as e:
        print(f"❌ Erro ao enviar e-mail: {e}")
        raise  # Repassa o erro para ser tratado na função chamadora

def utilizar_token(cd_alterar_senha):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        cursor.execute("SELECT utilizado FROM alterar_senha WHERE cd_alterar_senha = %s", (cd_alterar_senha,))
        resultado = cursor.fetchone()
        estado_atual = resultado[0]
        
        if not resultado:
            return jsonify({"MSG225": enviar_mensagem_positiva("MSG225"), "cd_alterar_senha": cd_alterar_senha}), 204
        
        novo_estado = 'S'
        global utilizado
        if estado_atual == 'N':
            utilizado = 'N'
            cursor.execute("UPDATE alterar_senha SET utilizado = %s WHERE cd_alterar_senha = %s", (novo_estado, cd_alterar_senha))
            bd.commit()
            token_valido = (estado_atual == 'S')
            return jsonify({"MSG267": enviar_mensagem_positiva("MSG267")+f" Solicitação {cd_alterar_senha} alterada de '{estado_atual}' para '{novo_estado}' com sucesso!",
                            "tokenValido": token_valido}),201
        else:
            utilizado = 'S'
            return jsonify({"MSG268": enviar_mensagem_negativa("MSG268"), "cd_alterar_senha": cd_alterar_senha})
    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao alterar estado da atividade: {e}"}), 400
    finally:
        bd.close()

def alterar_senha(cd_usuario, nova_senha):
    bd = conectar_base_de_dados()
    cursor = bd.cursor()
    try:
        if utilizado == 'N':
            sql = "UPDATE usuario SET senha = AES_ENCRYPT(%s, %s) WHERE cd_usuario = %s"
            valores = (nova_senha, senha, cd_usuario)
            cursor.execute(sql, valores)
            bd.commit()
            # registra log de Alteração de Senha
            # registrar_log_alterar_senha('ASU', cd_usuario=cd_usuario)
            return jsonify({"MSG058": enviar_mensagem_positiva("MSG058")}), 200
        else:
            return jsonify({"MSG268": enviar_mensagem_negativa("MSG268")})
    except Exception as e:
        bd.rollback()
        return jsonify({"error": f"Erro ao alterar senha: {e}"}), 400
    finally:
        bd.close()