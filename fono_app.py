import streamlit as st
from datetime import date, datetime, timedelta
import io

# Configuração da página - Layout amplo para o celular e computador
st.set_page_config(page_title="FonoClinic v1.3 - Demo", page_icon="🩺", layout="wide")

st.title("🩺 FonoClinic v1.3 — Painel de Demonstração Local")
st.info("💡 Modo de visualização ativo: O banco de dados em nuvem foi isolado temporariamente para testes visuais.")

# --- MOTOR DE GERAÇÃO DE HORÁRIOS FIXOS (08:00 às 20:00 - 10 em 10 min) ---
horarios_disponiveis = []
hora_atual = datetime.strptime("08:00", "%H:%M")
hora_fim = datetime.strptime("20:00", "%H:%M")
while hora_atual <= hora_fim:
    horarios_disponiveis.append(hora_atual.strftime("%H:%M"))
    hora_atual += timedelta(minutes=10)

# Função interna para gerar as perguntas de Sim/Não com padrão em branco ("")
def pergunta_sim_nao(label, key, info_adicional=False, label_adicional="Detalhes"):
    col1, col2 = st.columns(2)
    with col1:
        resposta = st.radio(label, ["", "Sim", "Não"], index=0, key=key, horizontal=True)
    with col2:
        detalhe = ""
        if info_adicional and resposta == "Sim":
            detalhe = st.text_input(f"{label_adicional}", key=f"{key}_det")
    return resposta, detalhe

# AS 6 ABAS OFICIAIS DO SOFTWARE REORDENADAS POR USABILIDADE CLÍNICA
aba1, aba2, aba3, aba4, aba5, aba6 = st.tabs([
    "📋 Painel de Atendimento",
    "📅 Marcar Horário",
    "👤 Admitir Paciente (Cadastro)",
    "📝 Preencher Anamnese",
    "🗂️ Central do Paciente (Prontuário)",
    "📄 Laudos & PDFs"
])

# =====================================================================
# ABA 1: PAINEL DE ATENDIMENTO (MODO DEMO VISUAL)
# =====================================================================
with aba1:
    st.header("📋 Painel de Atendimento Diário (Demonstração)")
    st.write("Visualização da grade de compromissos unificada da clínica.")

    tipo_visao = st.radio(
        "Filtro de Escopo Temporal:",
        ["Ver por Dia", "Ver por Semana", "Ver por Mês", "Ver por Ano"],
        horizontal=True, key="radio_tipo_visao"
    )
    data_base = st.date_input("Data de Referência:", value=date.today(), key="painel_data_ref")
    
    # Criando agendamentos de teste apenas para a Dra. Michelle ver o visual na tela
    dados_agenda_sheets = [
        {"id_linha": "1", "paciente": "Arthur Silva (Paciente Teste)", "data": data_base.strftime("%d/%m/%Y"), "hora": "09:00", "status": "Agendado", "tipo_consulta": "Atendimento de Rotina", "obs": "Trazer caderno de exercícios"},
        {"id_linha": "2", "paciente": "Beatriz Souza (Paciente Teste)", "data": data_base.strftime("%d/%m/%Y"), "hora": "10:30", "status": "Atendido", "tipo_consulta": "Primeira Consulta / Triagem", "obs": "Avaliação de processamento auditivo"},
        {"id_linha": "3", "paciente": "Carlos Eduardo (Paciente Teste)", "data": data_base.strftime("%d/%m/%Y"), "hora": "14:00", "status": "Faltou", "tipo_consulta": "Anamnese", "obs": "Mãe avisou que ia atrasar"}
    ]

    st.subheader(f"📅 Consultas Simuladas para o Período Base")
    
    st.write("🖨️ **Exportação Rápida da Grade:**")
    if st.button("⚙️ Compilar Grade de Compromissos (PDF)", key="btn_pdf_agenda_dia"):
        st.info("Grade de compromissos compilada com sucesso no simulador!")
        pdf_agenda_buf = io.BytesIO()
        pdf_agenda_buf.write(b"Grade de Atendimentos FonoClinic Demo")
        st.download_button("📥 Baixar PDF da Grade", data=pdf_agenda_buf.getvalue(), file_name="agenda_demonstracao.pdf", mime="application/pdf")
    st.markdown("---")

    for ag in dados_agenda_sheets:
        with st.container(border=True):
            col_c1, col_c2, col_c3 = st.columns(3)
            with col_c1:
                st.markdown(f"### ⏰ **{ag.get('hora', '')}** — {ag.get('paciente', '')}")
                st.caption(f"📅 Data: {ag.get('data', '')} | Tipo: {ag.get('tipo_consulta', 'Atendimento')}")
                if ag.get("obs", ""): st.info(f"📝 Obs: {ag.get('obs', '')}")
            with col_c2:
                status_atual = ag.get("status", "Agendado")
                if status_atual == "Agendado": st.warning(f"🔹 Status: {status_atual}")
                elif status_atual == "Atendido": st.success(f"✅ Status: {status_atual}")
                else: st.error(f"❌ Status: {status_atual}")
            with col_c3:
                if status_atual == "Agendado":
                    col_b1, col_b2 = st.columns(2)
                    if col_b1.button("✅ Concluir Atendimento", key=f"concluir_{ag.get('id_linha')}"):
                        st.success("Simulação: Atendimento concluído visualmente!")
                    if col_b2.button("🚨 Registrar Falta", key=f"falta_{ag.get('id_linha')}"):
                        st.error("Simulação: Falta registrada visualmente!")
                else:
                    if st.button("🗑️ Desmarcar Horário", key=f"excluir_{ag.get('id_linha')}"):
                        st.info("Simulação: Horário liberado na grade.")

# =====================================================================
# ABA 2: MARCAR HORÁRIO (MODO DEMO VISUAL)
# =====================================================================
with aba2:
    st.header("📅 Agendamento e Controle de Horários Vagos")
    st.write("Demonstração da tela de configuração de horários individuais ou em grupo.")
    
    lista_pacientes_sheets = ["Arthur Silva (Teste)", "Beatriz Souza (Teste)", "Carlos Eduardo (Teste)"]

    col_ag1, col_ag2 = st.columns(2)
    with col_ag1:
        p_nome = st.selectbox("Selecione o Paciente para Agenda:", lista_pacientes_sheets, key="agenda_p_sel")
        data_inicio = st.date_input("Data da Consulta (ou Início):", value=date.today(), key="agenda_data_ini")
        hora_agend = st.selectbox("Selecione o Horário Desejado:", horarios_disponiveis, key="agenda_hora_sel")
        tipo_consulta = st.selectbox("Tipo de Consulta:", ["Atendimento de Rotina", "Primeira Consulta / Triagem", "Anamnese", "🚫 Bloqueio de Agenda / Compromisso"])

    with col_ag2:
        recorrencia = st.selectbox("Configurar Repetição / Recorrência:", ["Consulta Única", "Semanal (Todas as semanas)", "Mensal (Uma vez por mês)", "Anual (Uma vez por ano)"])
        qtd_repeticoes = st.number_input("Quantidade de repetições em lote:", min_value=1, value=1, step=1)
        obs_consulta = st.text_input("Observação Rápida para o dia:", key="agenda_obs")
        atendimento_grupo = st.checkbox("⚙️ Permitir Atendimento em Grupo neste horário", value=False)

    st.markdown("---")
    if st.button("🔍 Consultar Grade de Horários Vagos nesta Data"):
        st.write(f"📂 **Simulação: Analisando lacunas vazias para o dia {data_inicio.strftime('%d/%m/%Y')}...**")
        st.write("Disponíveis para teste: " + ", ".join(horarios_disponiveis[5:15]) + "...")

    if st.button("🗓️ Confirmar Agendamento Clínico", key="btn_fixar_agenda"):
        st.success(f"Sucesso! Agendamento simulado criado para {p_nome} às {hora_agend}!")

# =====================================================================
# ABA 3: ADMITIR PACIENTE (CADASTRO DEMO)
# =====================================================================
with aba3:
    st.header("👤 Admitir Novo Paciente (Demonstração)")
    nome_paciente = st.text_input("Nome Completo do Paciente (Obrigatório)", key="cad_nome_admissao").strip()
    
    col1, col2, col3 = st.columns(3)
    data_nasc = col1.date_input("Data de Nascimento", value=None, min_value=date(2000, 1, 1), key="cad_data_nasc")
    sexo = col2.selectbox("Sexo", ["", "Masculino", "Feminino", "Outro"], key="cad_sexo")
    apelido = col3.text_input("Apelido", key="cad_apelido")
    
    col4, col5, col6 = st.columns(3)
    naturalidade = col4.text_input("Naturalidade", key="cad_naturalidade")
    endereco = col5.text_input("Endereço Completo", key="cad_endereco")
    emergencia = col6.text_input("Em caso de emergência ligar para:", key="cad_emergencia")
    
    col7, col8, col9 = st.columns(3)
    estuda = col7.selectbox("Estuda?", ["", "Sim", "Não"], key="cad_estuda")
    turma = col8.text_input("Turma", key="cad_turma") if estuda == "Sim" else ""
    turno = col9.selectbox("Turno", ["", "Manhã", "Tarde", "Integral"], key="cad_turno") if estuda == "Sim" else ""
    
    col10, col11, col12 = st.columns(3)
    responsavel = col10.text_input("Nome do Responsável Legal", key="cad_responsavel")
    profissao = col11.text_input("Profissão do Responsável", key="cad_profissao")
    telefone = col12.text_input("Telefone de Contato", key="cad_telefone")

    if st.button("💾 Salvar Admissão do Paciente", key="btn_salvar_cadastro"):
        if not nome_paciente:
            st.error("Erro: O nome do paciente é obrigatório.")
        else:
            st.success(f"Simulação: Ficha cadastral de '{nome_paciente}' validada na interface!")

# =====================================================================
# ABA 4: PREENCHER ANAMNESE CLINICA (BRINQUEDO COMPLETO)
# =====================================================================
with aba4:
    st.header("📝 Avaliação Inicial e Anamnese (Demonstração)")
    pac_cadastrados = ["Arthur Silva (Teste)", "Beatriz Souza (Teste)", "Carlos Eduardo (Teste)"]

    paciente_anamnese = st.selectbox("Selecione o Paciente para Vincular a Anamnese:", pac_cadastrados, key="sel_pac_anamnese")
    
    with st.expander("📋 Queixa Principal e Histórico Clínico", expanded=True):
        queixa = st.text_area("Queixa Principal (O que te trouxe aqui?)")
        pergunta_sim_nao("Faz terapia com outros profissionais?", "ter_outros", True, "Quais?")
        diagnostico_txt = st.text_input("Tem diagnóstico?")
        pergunta_sim_nao("Alérgico:", "alergia", True, "Quais?")
        pergunta_sim_nao("Toma medicação:", "medicao", True, "Quais?")
        com_quem_passa = st.text_input("Com quem passa mais tempo:")
        pergunta_sim_nao("Pratica ou gosta de esportes:", "esportes")

    with st.expander("🦶 Marcos de Desenvolvimento e Rotina de Telas", expanded=False):
        col_m1, col_m2 = st.columns(2)
        idade_sentou = col_m1.text_input("Com qual idade sentou?")
        idade_andou = col_m2.text_input("Com qual idade andou?")
        st.markdown("---")
        idade_primeiras_palavras = st.text_input("Com qual idade falou as primeiras palavras?")
        como_se_comunica_atualmente = st.text_area("Como se comunica atualmente?")
        st.markdown("---")
        tempo_telas = st.selectbox("Tempo diário estimado de exposição a telas:", ["", "Não utiliza", "Até 1 hora por dia", "De 1 a 3 horas por dia", "De 3 a 5 horas por dia", "Mais de 5 horas por dia"])
        detalhe_telas = st.text_input("Quais conteúdos costuma assistir?")

    with st.expander("🚽 Autonomia, Alimentação e Desenvolvimento", expanded=False):
        pergunta_sim_nao("Usa Fralda?", "fralda")
        pergunta_sim_nao("Sabe pedir para ir ao banheiro?", "banheiro")
        amamentacao = st.text_input("Ele(a) mamou peito ou fórmula?")
        mastigacao_degluticao = st.text_area("Descreva a mastigação e deglutição:")

    st.markdown("---")
    realizada_com = st.text_input("Anamnese realizada com (Grau de parentesco):")

    if st.button("💾 Salvar Anamnese Expandida no Prontuário", key="btn_salvar_anamnese"):
        st.success(f"Simulação: Anamnese clínica de '{paciente_anamnese}' processada com sucesso!")

# =====================================================================
# ABA 5: CENTRAL DO PACIENTE (PASTA DIGITAL DEMO)
# =====================================================================
with aba5:
    st.header("🗂️ Central do Paciente — Prontuário Digital Único (Demonstração)")
    pacientes_lista_pasta = ["Arthur Silva (Teste)", "Beatriz Souza (Teste)", "Carlos Eduardo (Teste)"]

    paciente_pasta = st.selectbox("🗄️ Abrir Pasta do Paciente:", pacientes_lista_pasta, key="sel_paciente_pasta")
    
    # Criando dados fictícios fixos para a Dra. Michelle ver como as informações são organizadas
    id_data = {
        "nome": paciente_pasta,
        "data_nasc": "15/04/2018",
        "sexo": "Masculino",
        "responsavel": "Mariana Silva (Mãe)",
        "telefone": "(11) 98888-7777",
        "endereco": "Rua das Flores, 123 - Centro"
    }
    ana_data = {
        "queixa": "Atraso na fala e troca de fonemas (/r/ por /l/)",
        "idade_sentou": "6 meses",
        "idade_andou": "1 ano e 1 mês",
        "idade_fala": "2 anos e 4 meses"
    }
    evolucoes_paciente = [
        {"data": "10/08/2026 14:30", "tipo": "Evolução de Atendimento de Rotina", "numero_consulta": "3", "texto": "Paciente apresentou excelente engajamento nas atividades lúdicas de estimulação do fonema /r/ vibrante. Boa resposta visual.", "link_midia": ""},
        {"data": "03/08/2026 14:15", "tipo": "Evolução de Atendimento de Rotina", "numero_consulta": "2", "texto": "Trabalhado sopro e motricidade orofacial. Apresenta ligeira hipotonia labial inferior.", "link_midia": "https://google.com"},
        {"data": "27/07/2026 14:00", "tipo": "Laudo de Exame Externo / Anexo Clínico", "numero_consulta": "", "texto": "Anexado exame de audiometria tonal e vocal. Limiares auditivos dentro da normalidade.", "link_midia": ""}
    ]

    sub_aba_id, sub_aba_clinica, sub_aba_historico = st.tabs(["📋 Dados de Cadastro & Anamnese", "📝 Evoluções & Laudos de Exames", "📈 Linha do Tempo e Alertas"])
    
    with sub_aba_id:
        st.subheader("👤 Ficha Cadastral de Admissão")
        col_d1, col_d2, col_d3 = st.columns(3)
        col_d1.write(f"**Nome:** {id_data.get('nome', '')}")
        col_d2.write(f"**Data de Nasc:** {id_data.get('data_nasc', '')}")
        col_d3.write(f"**Sexo:** {id_data.get('sexo', '')}")
        
        col_d4, col_d5, col_d6 = st.columns(3)
        col_d4.write(f"**Responsável Legal:** {id_data.get('responsavel', '')}")
        col_d5.write(f"**Telefone:** {id_data.get('telefone', '')}")
        col_d6.write(f"**Endereço:** {id_data.get('endereco', '')}")
        
        st.markdown("---")
        st.subheader("📝 Dados Extraídos da Anamnese")
        st.write(f"**Queixa Principal:** {ana_data.get('queixa', '')}")
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.write(f"**Sentou com:** {ana_data.get('idade_sentou', '—')}")
        col_m2.write(f"**Andou com:** {ana_data.get('idade_andou', '—')}")
        col_m3.write(f"**Falou com:** {ana_data.get('idade_fala', '—')}")

    with sub_aba_clinica:
        st.subheader("✍️ Novo Lançamento Clínico")
        tipo_registro = st.selectbox("Categoria do Documento:", ["Evolução de Atendimento de Rotina", "Relatório de Atendimento Concluído", "Laudo de Exame Externo / Anexo Clínico"], key="pasta_tipo_reg")
        texto_clinico = st.text_area("Descreva o parecer fonoaudiológico:", key="pasta_txt_clinico")
        link_midia = st.text_input("🔗 Link do Vídeo/Áudio de Evolução (Opcional):", key="pasta_link_midia")
        
        if st.button("💾 Arquivar na Pasta Digital (Simulação)", key="btn_pasta_salvar"):
            if not texto_clinico.strip(): 
                st.error("Digite o texto antes de arquivar.")
            else:
                st.success("Simulação: Documento clínico arquivado com sucesso no painel temporário!")
        
        st.markdown("---")
        for ev in reversed(evolucoes_paciente):
            tipo_ev = str(ev.get("tipo", ""))
            with st.chat_message("medical" if "Exame" in tipo_ev else "user"):
                num_str = str(ev.get("numero_consulta", ""))
                etiqueta = f" (Atendimento Nº {num_str})" if num_str else ""
                st.write(f"📅 **{ev.get('data', '')}** — *{tipo_ev}*{etiqueta}")
                st.info(ev.get("texto", ""))
                if ev.get("link_midia", ""):
                    st.caption(f"🔗 Mídia anexada: {ev.get('link_midia')}")

    with sub_aba_historico:
        st.subheader("📈 Linha do Tempo e Indicadores do Caso")
        
        realizadas = 12
        faltas_totais = 2
        
        col_m1, col_m2 = st.columns(2)
        col_m1.metric(label="✨ Total de Consultas Realizadas (Histórico)", value=f"{realizadas} sessões")
        col_m2.metric(label="🚨 Total de Faltas Registradas para Teste", value=f"{faltas_totais} faltas")
        
        if faltas_totais >= 2:
            st.error(f"⚠️ **Alerta Clínico de Absenteísmo:** O paciente '{paciente_pasta}' já acumulou {faltas_totais} faltas na simulação. Recomenda-se verificar a continuidade terapêutica.")
        
        st.markdown("---")
        st.subheader("🖨️ Exportação Rápida do Prontuário")
        st.write("Gere e baixe a ficha completa simulada com apenas um clique.")
        if st.button("⚙️ Compilar Prontuário Completo (PDF)", key="btn_pdf_direto_pasta"):
            st.info("Prontuário de teste compilado com sucesso!")
            pdf_buf = io.BytesIO()
            pdf_buf.write(b"Prontuario Completo FonoClinic Demo")
            st.download_button("📥 Baixar PDF do Prontuário", data=pdf_buf.getvalue(), file_name=f"prontuario_{paciente_pasta.lower().replace(' ', '_')}.pdf", mime="application/pdf")

# =====================================================================
# ABA 6: LAUDOS & PDFS (MODO DEMO VISUAL)
# =====================================================================
with aba6:
    st.header("📄 Emissão de Documentos e Relatórios em PDF")
    
    tipo_doc = st.selectbox("Selecione o Documento para Gerar PDF:", [
        "Laudo Fonoaudiológico", 
        "Atestado de Comparecimento", 
        "Recibo",
        "Espelho da Anamnese Completa",
        "Histórico Clínico e Evoluções"
    ], key="sel_tipo_pdf")
    
    if tipo_doc == "Laudo Fonoaudiológico":
        st.text_input("Nome do Paciente:", key="pdf_laudo_nome", value="Arthur Silva")
        st.text_input("Código CID:", key="pdf_laudo_cid", value="F80.0")
        st.text_area("Parecer Técnico Fonoaudiológico:", key="pdf_laudo_parecer", value="Paciente apresenta distúrbio fonológico marcado pela omissão...")
    elif tipo_doc == "Atestado de Comparecimento":
        st.text_input("Nome do Paciente:", key="pdf_atest_nome", value="Arthur Silva")
        st.date_input("Data do Comparecimento", value=date.today(), key="pdf_atest_data")
        st.text_input("Horário do Atendimento:", key="pdf_atest_hora", value="14:00 às 14:50")
    elif tipo_doc == "Recibo":
        st.text_input("Recebi de (Nome):", key="pdf_recibo_nome", value="Mariana Silva")
        st.number_input("Valor Cobrado (R$):", min_value=0.0, value=150.00, format="%.2f", key="pdf_recibo_valor")
        st.text_input("Valor por Extenso:", key="pdf_recibo_extenso", value="Cento e cinquenta reais")
    elif tipo_doc in ["Espelho da Anamnese Completa", "Histórico Clínico e Evoluções"]:
        st.selectbox("Puxar Dados do Paciente para Relatório:", pacientes_lista_pasta, key="pdf_p_sel")

    if st.button("⚙️ Gerar PDF Oficial", key="btn_generar_pdf_oficial"):
        st.info(f"O documento '{tipo_doc}' foi processado com sucesso na simulação local.")
        pdf_buffer = io.BytesIO()
        pdf_buffer.write(b"PDF Base FonoClinic v1.3")
        st.download_button(
            "📥 Baixar Arquivo PDF para Impressão", 
            data=pdf_buffer.getvalue(), 
            file_name=f"{tipo_doc.lower().replace(' ', '_')}.pdf", 
            mime="application/pdf",
            key="btn_download_pdf"
        )
