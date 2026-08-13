"""
FonoClinic V1.3 - Prontuário Eletrônico, Gestão Clínica e Agenda
Autor: Marcio de Andrade Neves & ADS Inteligência Co-Piloto
Versão: V1.3 (Repositório Isolado e Exclusivo)
Ano: 2026
"""

import streamlit as st
import pandas as pd
import numpy as np
import os
import io
from datetime import datetime

# Componentes estruturais do motor de PDF
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(page_title="FonoClinic v1.3", page_icon="🩺", layout="wide")

# ===================================================================
# 1. ARQUITETURA DE BANCO DE DADOS CLÍNICO (PERSISTÊNCIA EM 3 CSVs)
# ===================================================================
ARQUIVO_PACIENTES = "clinica_pacientes.csv"
ARQUIVO_EVOLUCOES = "clinica_evolucoes.csv"
ARQUIVO_AGENDA = "clinica_agenda.csv"

def inicializar_banco_clinico():
    # Tabela de Cadastro e Anamnese Expandida
    if not os.path.exists(ARQUIVO_PACIENTES) or os.path.getsize(ARQUIVO_PACIENTES) == 0:
        colunas_pac = [
            "ID", "Nome", "Data_Nascimento", "Responsavel", "Telefone", 
            "Queixa_Principal", "Historico_Medico", "Diagnostico_Fono", "Objetivos_Tratamento",
            "Marcos_Desenvolvimento", "Historico_Escolar", "Aspectos_Auditivos", "Sono_Alimentacao",
            "Possui_Atestado_Medico", "CID_Atestado", "Sessoes_Contratadas"
        ]
        pd.DataFrame(columns=colunas_pac).to_csv(ARQUIVO_PACIENTES, index=False)
        
    # Tabela de Sessões e Evolução Contínua
    if not os.path.exists(ARQUIVO_EVOLUCOES) or os.path.getsize(ARQUIVO_EVOLUCOES) == 0:
        colunas_evo = ["ID_Evolucao", "ID_Paciente", "Data_Sessao", "Evolucao_Detalhada", "Plano_Proxima_Sessao"]
        pd.DataFrame(columns=colunas_evo).to_csv(ARQUIVO_EVOLUCOES, index=False)
        
    # Tabela de Agenda de Consultas Marcadas
    if not os.path.exists(ARQUIVO_AGENDA) or os.path.getsize(ARQUIVO_AGENDA) == 0:
        colunas_age = ["ID_Agendamento", "Paciente_Nome", "Data_Agendada", "Horario", "Status"]
        pd.DataFrame(columns=colunas_age).to_csv(ARQUIVO_AGENDA, index=False)

inicializar_banco_clinico()

# ===================================================================
# 2. FUNÇÕES UTILITÁRIAS GLOBAIS (IDADE E MOTOR PDF)
# ===================================================================
def calcular_idade_detalhada(data_nasc_str):
    try:
        nasc = datetime.strptime(data_nasc_str, "%Y-%m-%d")
        hoje = datetime.today()
        anos = hoje.year - nasc.year
        meses = hoje.month - nasc.month
        if hoje.day < nasc.day:
            meses -= 1
        if meses < 0:
            anos -= 1
            meses += 12
        return f"{anos} anos e {meses} meses"
    except Exception:
        return "Idade nao calculada"

def gerar_pdf_relatorio(titulo_doc, texto_conteudo):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()
    
    style_titulo = ParagraphStyle('TituloFono', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor('#2c3e50'), spaceAfter=15)
    style_corpo = ParagraphStyle('CorpoFono', parent=styles['Normal'], fontSize=11, leading=16, spaceAfter=8)
    
    story = []
    story.append(Paragraph(f"<b>{titulo_doc}</b>", style_titulo))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", style_corpo))
    story.append(Paragraph(f"Profissional Responsavel: Fonoaudiologa Cadastrada", style_corpo))
    story.append(Spacer(1, 15))
    
    for linha in texto_conteudo.split('\n'):
        linha_limpa = linha.strip()
        if linha_limpa:
            linha_limpa = linha_limpa.encode('ascii', 'ignore').decode('ascii')
            linha_limpa = linha_limpa.replace("&", "&amp;").replace("< ", "&lt; ").replace(" >", " &gt;")
            try:
                story.append(Paragraph(linha_limpa, style_corpo))
            except Exception:
                story.append(Paragraph("Dado ocultado por caractere invalido.", style_corpo))
            
    doc.build(story)
    buffer.seek(0)
    return buffer

# ===================================================================
# 3. INTERFACE PRINCIPAL E NAVEGAÇÃO DE ABAS EXPANDIDA
# ===================================================================
st.title("🩺 FonoClinic v1.3 — Prontuário, Gestão & Agenda Integrada")
st.markdown("---")

aba_cadastro, aba_prontuario, aba_relatorios, aba_agenda = st.tabs([
    "📝 Nova Anamnese / Cadastro", 
    "🗂️ Consultar Prontuário & Evolução", 
    "📋 Emitir Laudos & Recibos (PDF)",
    "📅 Agenda de Consultas"
])

# ---------------------------------------------------------------
# ABA 1: NOVA ANAMNESE EXPANDIDA E GERENCIAMENTO DE SESSÕES
# ---------------------------------------------------------------
with aba_cadastro:
    st.subheader("Formulário de Entrada e Anamnese Fonoaudiológica Completa")
    
    with st.form("form_anamnese", clear_on_submit=False):
        # Seção 1: Dados Cadastrais e Administrativos
        st.markdown("##### 👥 Dados Identificatórios e Contrato")
        col1, col2, col3 = st.columns(3)
        with col1:
            f_nome = st.text_input("Nome Completo do Paciente:")
            f_nasc = st.date_input("Data de Nascimento:", min_value=datetime(1920, 1, 1), value=datetime(2020, 1, 1))
        with col2:
            f_resp = st.text_input("Nome do Responsável (Se menor):")
            f_tel = st.text_input("Telefone de Contato:")
        with col3:
            f_sessoes = st.number_input("Número de Sessões Contratadas (Pacote):", min_value=1, max_value=100, value=10)
            
        st.markdown("---")
        
        # Seção 2: Histórico Clínico Médico e Documentação Externa
        st.markdown("##### 🏥 Histórico Médico e Triagem de Entrada")
        col_med1, col_med2 = st.columns(2)
        with col_med1:
            f_atestado = st.selectbox("O paciente possui encaminhamento/atestado médico?", ["Não", "Sim"])
        with col_med2:
            f_cid = st.text_input("Código CID informado no documento (Se houver):", value="N/A")
            
        f_queixa = st.text_area("Queixa Principal (O que trouxe o paciente à clínica?):", height=60)
        f_historico = st.text_area("Histórico Médico relevante (Marcos de saúde, exames, internações):", height=60)
        
        st.markdown("---")
        
        # Seção 3: Perguntas Clínicas Especializadas em Fonoaudiologia
        st.markdown("##### 🧠 Módulo Avançado de Anamnese Fonoaudiológica")
        col_fono1, col_fono2 = st.columns(2)
        with col_fono1:
            f_marcos = st.text_area("Marcos do Desenvolvimento (Fala, marcha, sustentação cefálica):", height=60)
            f_audicao = st.text_area("Aspectos Auditivos (Reação a sons, histórico de otites, exames de audição):", height=60)
        with col_fono2:
            f_escola = st.text_area("Histórico Escolar (Comportamento, aprendizado, socialização):", height=60)
            f_sono = st.text_area("Rotinas de Sono e Alimentação (Mastigação, deglutição, seletividade):", height=60)
            
        st.markdown("---")
        f_diag = st.text_area("Hipótese Diagnóstica / Diagnóstico Fonoaudiológico Inicial:", height=60)
        f_obj = st.text_area("Objetivos Iniciais do Tratamento Terapêutico:", height=60)
        
        btn_salvar = st.form_submit_button("💾 Salvar Prontuário e Iniciar Tratamento")
        
        if btn_salvar:
            nome_limpo = f_nome.strip()
            tel_limpo = f_tel.strip()
            
            if nome_limpo and tel_limpo:
                df_existente = pd.read_csv(ARQUIVO_PACIENTES)
                
                # Controle estrito antiduplicidade
                if not df_existente.empty and nome_limpo.lower() in df_existente["Nome"].str.lower().values:
                    st.warning(f"⚠️ Atenção: Já existe um paciente cadastrado com o nome `{nome_limpo}`. Evite cadastros duplicados.")
                else:
                    novo_id = int(df_existente["ID"].max() + 1) if not df_existente.empty else 1001
                    
                    nova_linha = {
                        "ID": novo_id, "Nome": nome_limpo, "Data_Nascimento": str(f_nasc),
                        "Responsavel": f_resp if f_resp.strip() else "O Próprio", "Telefone": tel_limpo,
                        "Queixa_Principal": f_queixa, "Historico_Medico": f_historico,
                        "Diagnostico_Fono": f_diag, "Objetivos_Tratamento": f_obj,
                        "Marcos_Desenvolvimento": f_marcos, "Historico_Escolar": f_escola,
                        "Aspectos_Auditivos": f_audicao, "Sono_Alimentacao": f_sono,
                        "Possui_Atestado_Medico": f_atestado, "CID_Atestado": f_cid.strip().upper(),
                        "Sessoes_Contratadas": int(f_sessoes)
                    }
                    
                    df_novo = pd.concat([df_existente, pd.DataFrame([nova_linha])], ignore_index=True)
                    df_novo.to_csv(ARQUIVO_PACIENTES, index=False)
                    
                    idade_calculada = calcular_idade_detalhada(str(f_nasc))
                    st.success(f"🎉 Prontuário Clínico de `{nome_limpo}` ({idade_calculada}) criado com sucesso! ID: **{novo_id}** | Pacote Inicial: **{f_sessoes} sessões**")
            else:
                st.error("⚠️ Erro: Os campos 'Nome' e 'Telefone' são obrigatórios para a abertura da ficha de anamnese.")

# ---------------------------------------------------------------
# ABA 2: CONSULTAR PRONTUÁRIO & EVOLUÇÃO CONTÍNUA (COM CONTROLE DE PACOTES)
# ---------------------------------------------------------------
with aba_prontuario:
    st.subheader("Painel de Acompanhamento Clínico Avançado")
    
    if os.path.exists(ARQUIVO_PACIENTES) and os.path.getsize(ARQUIVO_PACIENTES) > 0:
        df_pac = pd.read_csv(ARQUIVO_PACIENTES)
    else:
        df_pac = pd.DataFrame()
        
    if df_pac.empty:
        st.info("💡 Nenhum paciente cadastrado ainda. Use a primeira aba para realizar a primeira anamnese.")
    else:
        lista_pacientes = df_pac["Nome"].tolist()
        paciente_selecionado = st.selectbox("Selecione o Paciente para abrir o Prontuário:", lista_pacientes)
        
        dados_pac = df_pac[df_pac["Nome"] == paciente_selecionado].iloc[0]
        id_paciente = dados_pac["ID"]
        
        # Idade dinâmica e verificação de sessões contratadas
        idade_paciente_atual = calcular_idade_detalhada(str(dados_pac['Data_Nascimento']))
        sessoes_contratadas = int(dados_pac["Sessoes_Contratadas"]) if "Sessoes_Contratadas" in df_pac.columns else 10
        
        # Carrega o histórico de sessões para o contador e exibição
        if os.path.exists(ARQUIVO_EVOLUCOES) and os.path.getsize(ARQUIVO_EVOLUCOES) > 0:
            df_evo = pd.read_csv(ARQUIVO_EVOLUCOES)
            df_evo_pac = df_evo[df_evo["ID_Paciente"] == id_paciente]
        else:
            df_evo_pac = pd.DataFrame()
            
        sessoes_realizadas = len(df_evo_pac)
        sessoes_restantes = max(0, sessoes_contratadas - sessoes_realizadas)
        
        # Painel Visual de Status e Informações Rápidas
        col_p1, col_p2, col_p3 = st.columns(3)
        with col_p1:
            st.markdown(f"**ID Único:** `{id_paciente}`")
            st.markdown(f"👤 **Nome:** {dados_pac['Nome']}")
            st.markdown(f"📞 **Telefone:** {dados_pac['Telefone']}")
        with col_p2:
            st.markdown(f"📅 **Nascimento:** {dados_pac['Data_Nascimento']}")
            st.markdown(f"⏳ **Idade Atual:** `{idade_paciente_atual}`")
            st.markdown(f"👥 **Responsável:** {dados_pac['Responsavel']}")
        with col_p3:
            # Painel do Contador Automático de Pacotes/Sessões
            st.markdown("##### 📊 Controle de Pacote de Sessões")
            st.metric(label="Sessões Realizadas", value=f"{sessoes_realizadas} / {sessoes_contratadas}")
            if sessoes_restantes == 0:
                st.error("🚨 Atenção: Pacote esgotado! Contrate novas sessões.")
            elif sessoes_restantes <= 2:
                st.warning(f"⚠️ Restam apenas {sessoes_restantes} sessões.")
            else:
                st.success(f"✅ Restam {sessoes_restantes} sessões no pacote.")
            
        st.markdown("---")
        
        # Ficha Clínica Completa com Menus Retráteis
        st.markdown("##### 🔍 Histórico Completo da Anamnese")
        exp_cad = st.expander("📄 Dados Médicos e Entrada Geral", expanded=False)
        with exp_cad:
            st.write(f"**Queixa Principal:** {dados_pac['Queixa_Principal']}")
            st.write(f"**Histórico Médico:** {dados_pac['Historico_Medico']}")
            st.write(f"**Possui Atestado/Encaminhamento?** {dados_pac.get('Possui_Atestado_Medico', 'Não')} | **Código CID:** `{dados_pac.get('CID_Atestado', 'N/A')}`")
            
        exp_fono = st.expander("🧠 Dados Fonoaudiológicos Especializados", expanded=False)
        with exp_fono:
            st.write(f"**Marcos do Desenvolvimento:** {dados_pac.get('Marcos_Desenvolvimento', 'Não informado')}")
            st.write(f"**Aspectos Auditivos:** {dados_pac.get('Aspectos_Auditivos', 'Não informado')}")
            st.write(f"**Histórico Escolar:** {dados_pac.get('Historico_Escolar', 'Não informado')}")
            st.write(f"**Rotinas de Sono e Alimentação:** {dados_pac.get('Sono_Alimentacao', 'Não informado')}")
            st.write(f"**Diagnóstico Inicial:** {dados_pac['Diagnostico_Fono']}")
            st.write(f"**Objetivos Terapêuticos:** {dados_pac['Objetivos_Tratamento']}")
            
        st.markdown("### 📘 Diário de Evolução Terapêutica")
        
        if not df_evo_pac.empty:
            df_evo_pac = df_evo_pac.sort_values(by="Data_Sessao", ascending=False)
            for idx_e, linha_e in df_evo_pac.iterrows():
                st.info(f"**Sessão em {linha_e['Data_Sessao']}:**  \n"
                        f"• **Evolução:** {linha_e['Evolucao_Detalhada']}  \n"
                        f"• **Conduta/Próxima Sessão:** {linha_e['Plano_Proxima_Sessao']}")
        else:
            st.warning("Nenhuma sessão registrada para este paciente.")
            
        st.markdown("---")
        st.markdown("#### 📝 Registrar Nova Sessão (Evolução Diária)")
        
        with st.form("form_evolucao", clear_on_submit=True):
            col_e1, col_e2 = st.columns(2)
            with col_e1:
                e_data = st.date_input("Data do Atendimento:", value=datetime.today())
            with col_e2:
                e_detalhe = st.text_area("O que foi trabalhado na sessão? (Evolução clínica):")
                
            e_plano = st.text_input("Planejamento / Conduta para a próxima sessão:")
            btn_evolucao = st.form_submit_button("➕ Gravar Evolução da Sessão")
            
            if btn_evolucao:
                if e_detalhe.strip():
                    df_evo_existente = pd.read_csv(ARQUIVO_EVOLUCOES) if os.path.exists(ARQUIVO_EVOLUCOES) else pd.DataFrame()
                    novo_id_evo = int(df_evo_existente["ID_Evolucao"].max() + 1) if (not df_evo_existente.empty and "ID_Evolucao" in df_evo_existente.columns) else 5001
                    
                    nova_evo = {
                        "ID_Evolucao": novo_id_evo,
                        "ID_Paciente": int(id_paciente),
                        "Data_Sessao": str(e_data),
                        "Evolucao_Detalhada": e_detalhe.strip(),
                        "Plano_Proxima_Sessao": e_plano.strip() if e_plano.strip() else "Manter conduta"
                    }
                    
                    df_novo_evo = pd.concat([df_evo_existente, pd.DataFrame([nova_evo])], ignore_index=True)
                    df_novo_evo.to_csv(ARQUIVO_EVOLUCOES, index=False)
                    st.success("🎯 Evolução registrada com sucesso no prontuário!")
                    st.rerun()
                else:
                    st.error("⚠️ Insira os detalhes do atendimento antes de salvar.")

# ---------------------------------------------------------------
# ABA 3: EMISSÃO DE RELATÓRIOS TÉCNICOS, LAUDOS E RECIBOS EM PDF
# ---------------------------------------------------------------
with aba_relatorios:
    st.subheader("Gerador de Documentos Clínicos e Administrativos Oficiais")
    st.markdown("Selecione o paciente para gerar o documento PDF formatado para impressão.")
    
    if os.path.exists(ARQUIVO_PACIENTES) and os.path.getsize(ARQUIVO_PACIENTES) > 0:
        df_pac_rep = pd.read_csv(ARQUIVO_PACIENTES)
    else:
        df_pac_rep = pd.DataFrame()
        
    if df_pac_rep.empty:
        st.info("💡 Cadastre um paciente para habilitar a emissao de laudos em PDF.")
    else:
        lista_pac_rep = df_pac_rep["Nome"].tolist()
        pac_rep_sel = st.selectbox("Selecione o Paciente para o Documento:", lista_pac_rep, key="rep_sel")
        
        dados_r = df_pac_rep[df_pac_rep["Nome"] == pac_rep_sel].iloc[0]
        id_r = dados_r["ID"]
        
        tipo_doc = st.radio(
            "Selecione o Tipo de Documento que deseja gerar:", 
            ["Relatorio de Evolucao Fonoaudiologica", "Laudo Fonoaudiológico", "Recibo de Atendimento Clinico", "Atestado de Comparecimento"]
        )
        
        st.markdown("---")
        
        texto_adicional = ""
        if "Recibo" in tipo_doc:
            col_rec1, col_ind_v = st.columns(2)
            with col_rec1:
                v_sessao = st.text_input("Valor da Sessao (Ex: R$ 150,00):", value="R$ 150,00")
            with col_ind_v:
                v_extenso = st.text_input("Valor por Extenso (Ex: Cento e cinquenta reais):", value="Cento e cinquenta reais")
            
            texto_adicional = (
                f"Declaramos para os devidos fins de direito que recebemos a importancia de {v_extenso} ({v_sessao}), "
                f"referente aos servicos prestados de atendimento fonoaudiologico para o paciente citado acima."
            )
        elif "Atestado" in tipo_doc:
            col_at1, col_at2 = st.columns(2)
            with col_at1:
                h_inicio = st.text_input("Horario de Inicio (Ex: 14:00):", value="14:00")
            with col_at2:
                h_fim = st.text_input("Horario de Termino (Ex: 15:00):", value="15:00")
                
            texto_adicional = (
                f"Atestamos para os devidos fins que o paciente esteve em atendimento fonoaudiologico na data de hoje, "
                f"no periodo das {h_inicio} as {h_fim} horas, devendo a presente declaracao ser considerada para justificativa de ausencia."
            )
        else:
            texto_adicional = st.text_area("Observacoes Clinicas Adicionais / Recomendacoes (Opcional):", height=80)
        
        if st.button("🖨️ Compilar e Emitir Documento Oficial"):
            try:
                historico_sessoes = ""
                if "Relatorio" in tipo_doc or "Laudo" in tipo_doc:
                    if os.path.exists(ARQUIVO_EVOLUCOES) and os.path.getsize(ARQUIVO_EVOLUCOES) > 0:
                        df_ev_rep = pd.read_csv(ARQUIVO_EVOLUCOES)
                        df_ev_rep = df_ev_rep[df_ev_rep["ID_Paciente"] == id_r].sort_values(by="Data_Sessao", ascending=True)
                        
                        if not df_ev_rep.empty:
                            historico_sessoes = "\n\nHISTORICO DE EVOLUCAO CLINICA:\n"
                            for _, lin_ev in df_ev_rep.iterrows():
                                historico_sessoes += f"- Data: {lin_ev['Data_Sessao']} | Evolucao: {lin_ev['Evolucao_Detalhada']} | Proxima Sessao: {lin_ev['Plano_Proxima_Sessao']}\n"
                        else:
                            historico_sessoes = "\n\nNenhuma sessao registrada no diario de evolucao ate a presente data."
                
                idade_doc = calcular_idade_detalhada(str(dados_r['Data_Nascimento']))
                corpo_laudo = (
                    f"DADOS DO PACIENTE:\n"
                    f"Nome Completo: {dados_r['Nome']}\n"
                    f"Data de Nascimento: {dados_r['Data_Nascimento']} (Idade: {idade_doc})\n"
                    f"Responsavel Legal: {dados_r['Responsavel']}\n"
                    f"Telefone de Contato: {dados_r['Telefone']}\n\n"
                )
                
                if "Relatorio" in tipo_doc or "Laudo" in tipo_doc:
                    corpo_laudo += (
                        f"AVALIACAO CLINICA INICIAL:\n"
                        f"Queixa Principal: {dados_r['Queixa_Principal']}\n"
                        f"Historico Medico/Anamnese: {dados_r['Historico_Medico']}\n"
                        f"Encaminhamento Medico: {dados_r.get('Possui_Atestado_Medico', 'Nao')} | Codigo CID: {dados_r.get('CID_Atestado', 'N/A')}\n\n"
                        f"ANAMNESE FONOAUDIOLOGICA EXPANDIDA:\n"
                        f"- Marcos do Desenvolvimento: {dados_r.get('Marcos_Desenvolvimento', 'N/A')}\n"
                        f"- Aspectos Auditivos: {dados_r.get('Aspectos_Auditivos', 'N/A')}\n"
                        f"- Historico Escolar: {dados_r.get('Historico_Escolar', 'N/A')}\n"
                        f"- Sono e Alimentacao: {dados_r.get('Sono_Alimentacao', 'N/A')}\n\n"
                        f"DIAGNOSTICO E DIRETRIZES:\n"
                        f"Diagnostico Inicial: {dados_r['Diagnostico_Fono']}\n"
                        f"Objetivos Terapeuticos: {dados_r['Objetivos_Tratamento']}"
                        f"{historico_sessoes}"
                    )
                    if texto_adicional.strip():
                        corpo_laudo += f"\n\nOBSERVACOES E RECOMENDACOES ADICIONAIS:\n{texto_adicional.strip()}"
                else:
                    corpo_laudo += f"CONTEUDO DECLARATORIO:\n{texto_adicional.strip()}"
                    
                corpo_laudo += f"\n\n\n\n_________________________________________\nAssinatura e Carimbo da Fonoaudiologa"
                
                pdf_gerado = gerar_pdf_relatorio(tipo_doc.upper(), corpo_laudo)
                
                st.success(f"🎯 Documento `{tipo_doc}` gerado com sucesso!")
                st.download_button(
                    "📥 Baixar Documento em PDF", 
                    pdf_gerado, 
                    f"{tipo_doc.lower().replace(' ', '_')}_{dados_r['Nome'].lower().replace(' ', '_')}.pdf", 
                    "application/pdf"
                )
                
            except Exception as ex_rep:
                st.error(f"Erro ao compilar documento: {str(ex_rep)}")

    # ---------------------------------------------------------------
    # ABA 4: GESTÃO DE AGENDA CLÍNICA SEMANAL
    # ---------------------------------------------------------------
    with aba_agenda:
        st.subheader("控制 - 📅 Controle de Agendamentos e Horários")
        
        if os.path.exists(ARQUIVO_AGENDA) and os.path.getsize(ARQUIVO_AGENDA) > 0:
            df_agenda = pd.read_csv(ARQUIVO_AGENDA)
        else:
            df_agenda = pd.DataFrame()

        col_ag1, col_age2 = st.columns(2)
        
        with col_ag1:
            st.markdown("##### 📝 Novo Agendamento")
            with st.form("form_agenda", clear_on_submit=True):
                if os.path.exists(ARQUIVO_PACIENTES) and os.path.getsize(ARQUIVO_PACIENTES) > 0:
                    lista_nomes_pac = pd.read_csv(ARQUIVO_PACIENTES)["Nome"].tolist()
                else:
                    lista_nomes_pac = ["Cadastre um paciente primeiro"]
                    
                ag_paciente = st.selectbox("Selecione o Paciente:", lista_nomes_pac)
                ag_data = st.date_input("Data da Consulta:", value=datetime.today())
                ag_hora = st.text_input("Horário (Ex: 14:00):", value="14:00")
                ag_status = st.selectbox("Status Inicial:", ["Agendado", "Atendido", "Faltou"])
                
                btn_agendar = st.form_submit_button("📅 Confirmar Horário")
                
                if btn_agendar:
                    if ag_paciente != "Cadastre um paciente primeiro" and ag_hora.strip():
                        novo_id_ag = int(df_agenda["ID_Agendamento"].max() + 1) if (not df_agenda.empty and "ID_Agendamento" in df_agenda.columns) else 8001
                        
                        novo_compromisso = {
                            "ID_Agendamento": novo_id_ag,
                            "Paciente_Nome": ag_paciente,
                            "Data_Agendada": str(ag_data),
                            "Horario": ag_hora.strip(),
                            "Status": ag_status
                        }
                        
                        df_agenda_nova = pd.concat([df_agenda, pd.DataFrame([novo_compromisso])], ignore_index=True)
                        df_agenda_nova.to_csv(ARQUIVO_AGENDA, index=False)
                        st.success(f"🗓️ Horário marcado para `{ag_paciente}`!")
                        st.rerun()
                    else:
                        st.error("⚠️ Erro ao agendar. Certifique-se de preencher o horário corretamente.")

        with col_age2:
            st.markdown("##### 📋 Listagem de Consultas Marcadas")
            if not df_agenda.empty:
                df_agenda_vis = df_agenda.sort_values(by=["Data_Agendada", "Horario"], ascending=True).reset_index(drop=True)
                st.dataframe(df_agenda_vis, use_container_width=True)
                
                with st.expander("❌ Cancelar / Remover Compromisso da Agenda", expanded=False):
                    id_cancelar = st.number_input("Digite o ID do Agendamento que deseja remover:", min_value=8001, step=1)
                    if st.button("Remover Horário Permanentemente"):
                        if id_cancelar in df_agenda["ID_Agendamento"].values:
                            df_agenda = df_agenda[df_agenda["ID_Agendamento"] != id_cancelar]
                            df_agenda.to_csv(ARQUIVO_AGENDA, index=False)
                            st.toast("Horário removido com sucesso!", icon="🗑️")
                            st.rerun()
                        else:
                            st.error("ID de agendamento não encontrado.")
            else:
                st.info("Nenhuma consulta agendada na semana.")

    # ---------------------------------------------------------------
    # PAINEL ADICIONAL: INDICADORES E MÉTRICAS DA CLÍNICA
    # ---------------------------------------------------------------
    st.markdown("---")
    st.subheader("📊 Indicadores de Atendimento da Clínica")
    
    col_ind1, col_ind2 = st.columns(2)
    with col_ind1:
        if os.path.exists(ARQUIVO_PACIENTES) and os.path.getsize(ARQUIVO_PACIENTES) > 0:
            total_pacientes = len(pd.read_csv(ARQUIVO_PACIENTES))
        else:
            total_pacientes = 0
        st.metric(label="👥 Total de Pacientes Ativos", value=total_pacientes)
    with col_ind2:
        if os.path.exists(ARQUIVO_EVOLUCOES) and os.path.getsize(ARQUIVO_EVOLUCOES) > 0:
            total_sessoes = len(pd.read_csv(ARQUIVO_EVOLUCOES))
        else:
            total_sessoes = 0
        st.metric(label="🎯 Total de Sessões Realizadas", value=total_sessoes)
        
    st.caption("FonoClinic v1.3 • Sistema integrado com controle de pacotes, CID, anamnese fonoaudiológica e agenda.")
