import streamlit as st
from datetime import date, datetime, timedelta
import io

# Configuração da página - Layout amplo para celular e computador
st.set_page_config(page_title="FonoClinic v1.5 - Final", page_icon="🩺", layout="wide")

st.title("🩺 FonoClinic v1.5 — Painel de Demonstração Avançado")
st.info("💡 Modo de visualização ativo: Banco de dados simulado localmente para validação clínica.")

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

# AS 7 ABAS OFICIAIS DO SOFTWARE REORDENADAS POR USABILIDADE CLÍNICA
aba1, aba2, aba3, aba4, aba5, aba6, aba7 = st.tabs([
    "📋 Painel de Atendimento",
    "📅 Marcar Horário",
    "👤 Admitir Paciente (Cadastro)",
    "📝 Triagem Inicial",
    "🗂️ Central do Paciente (Prontuário)",
    "📄 Laudos & PDFs",
    "📚 Anamnese Completa (Robusta)"
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
    
    # Criando agendamentos de teste apenas para ver o visual na tela
    dados_agenda_sheets = [
        {"id_linha": "1", "paciente": "Arthur Silva (Infantil - TEA)", "data": data_base.strftime("%d/%m/%Y"), "hora": "09:00", "status": "Agendado", "tipo_consulta": "Atendimento de Rotina", "obs": "Trazer caderno de exercícios"},
        {"id_linha": "2", "paciente": "Beatriz Souza (Infantil - Apraxia)", "data": data_base.strftime("%d/%m/%Y"), "hora": "10:30", "status": "Atendido", "tipo_consulta": "Primeira Consulta / Triagem", "obs": "Avaliação de processamento auditivo"},
        {"id_linha": "3", "paciente": "Carlos Eduardo (Adulto - Pós-AVC)", "data": data_base.strftime("%d/%m/%Y"), "hora": "14:00", "status": "Faltou", "tipo_consulta": "Anamnese", "obs": "Mãe avisou que ia atrasar"}
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
    
    lista_pacientes_sheets = ["Arthur Silva (Infantil - TEA)", "Beatriz Souza (Infantil - Apraxia)", "Carlos Eduardo (Adulto - Pós-AVC)"]

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
    if st.button("🔍 Consultar Grade de Horários Vagos nesta Data", key="btn_consultar_vagos"):
        st.write(f"📂 **Simulação: Analisando lacunas vazias para o dia {data_inicio.strftime('%d/%m/%Y')}...**")
        st.write("Disponíveis para teste: " + ", ".join(horarios_disponiveis[5:15]) + "...")

    if st.button("🗓️ Confirmar Agendamento Clínico", key="btn_fixar_agenda"):
        st.success(f"Sucesso! Agendamento simulado criado para {p_nome} às {hora_agend}!")

# =====================================================================
# ABA 3: ADMITIR PACIENTE (CADASTRO - MODO DEMO VISUAL ATUALIZADO)
# =====================================================================
with aba3:
    st.header("👤 Admitir Novo Paciente (Cadastro Inicial)")
    st.write("Formulário completo de dados demográficos, filiação e localização do paciente.")

    with st.form("form_cadastro_paciente"):
        st.subheader("1. Dados Pessoais e Filiação")
        col_cad1, col_cad2 = st.columns(2)
        with col_cad1:
            cad_nome = st.text_input("Nome Completo do Paciente:", placeholder="Digite o nome sem abreviações", key="cad_nome")
            cad_nasc = st.date_input("Data de Nascimento:", value=date(2015, 1, 1), key="cad_nasc")
            cad_genero = st.selectbox("Gênero Biológico / Identidade:", ["", "Masculino", "Feminino", "Outro"], key="cad_genero")
            cad_cpf = st.text_input("CPF do Paciente (ou Responsável):", placeholder="000.000.000-00", key="cad_cpf")
        
        with col_cad2:
            cad_mae = st.text_input("Nome Completo da Mãe:", placeholder="Nome completo da mãe", key="cad_mae")
            cad_pai = st.text_input("Nome Completo do Pai:", placeholder="Nome completo do pai", key="cad_pai")
            cad_resp = st.text_input("Responsável Legal (se não forem os pais):", placeholder="Obrigatório para menores de idade", key="cad_resp")
            cad_tel = st.text_input("Telefone / WhatsApp de Contato:", placeholder="(00) 00000-0000", key="cad_tel")

        st.markdown("---")
        st.subheader("2. Endereço Residencial")
        col_end1, col_end2, col_end3 = st.columns(3)
        with col_end1:
            cad_rua = st.text_input("Logradouro (Rua, Avenida, etc.):", placeholder="Ex: Rua das Flores", key="cad_rua")
        with col_end2:
            cad_num = st.text_input("Número:", placeholder="Ex: 123", key="cad_num")
        with col_end3:
            cad_compl = st.text_input("Complemento:", placeholder="Ex: Ap 402", key="cad_compl")

        col_end4, col_end5, col_end6 = st.columns(3)
        with col_end4:
            cad_bairro = st.text_input("Bairro:", placeholder="Ex: Centro", key="cad_bairro")
        with col_end5:
            cad_cidade = st.text_input("Cidade:", placeholder="Ex: Rio de Janeiro", key="cad_cidade")
        with col_end6:
            cad_uf = st.text_input("UF:", max_chars=2, placeholder="RJ", key="cad_uf")

        st.markdown("---")
        st.subheader("3. Informações Adicionais")
        cad_email = st.text_input("E-mail para Notificações:", placeholder="exemplo@email.com", key="cad_email")
        cad_obs = st.text_area("Observações Administrativas Importantes:", placeholder="Convênio, restrições de horários, etc.", key="cad_obs")

        st.markdown("---")
        btn_salvar_cadastro = st.form_submit_button("💾 Salvar Registro de Admissão")
        if btn_salvar_cadastro:
            if cad_nome:
                st.success(f"🎉 Sucesso! Registro de {cad_nome} com filiação e endereço simulado na base local.")
            else:
                st.warning("⚠️ Por favor, insira pelo menos o nome do paciente para testar.")

# =====================================================================
# ABA 4: PREENCHER ANAMNESE / TRIAGEM INICIAL (MODO DEMO VISUAL)
# =====================================================================
with aba4:
    st.header("📝 Questionário de Triagem Inicial Fonoaudiológica")
    st.write("Coleta resumida e rápida do histórico e queixas clínicas imediatas.")

    paciente_anamnese = st.selectbox("Selecionar Paciente para Vincular Triagem:", ["Arthur Silva (Infantil - TEA)", "Beatriz Souza (Infantil - Apraxia)", "Carlos Eduardo (Adulto - Pós-AVC)"], key="anamnese_p_sel")
    
    st.subheader("1. Queixa Principal e Histórico Inicial")
    queixa_principal = st.text_area("Qual a queixa principal da família ou do paciente?", placeholder="Ex: Atraso na fala, troca de fonemas, dificuldade de mastigação...", key="tri_queixa")
    historico_medico = st.text_area("Histórico médico relevante (Intervenções, diagnósticos prévios):", key="tri_historico")

    st.subheader("2. Desenvolvimento Motor e de Linguagem")
    resp_fala, det_fala = pergunta_sim_nao("Apresenta atraso no desenvolvimento da fala?", "anam_fala", info_adicional=True, label_adicional="Com quantos anos começou a falar?")
    resp_compreende, det_compreende = pergunta_sim_nao("Compreende ordens verbais simples?", "anam_comp")
    resp_andou, det_andou = pergunta_sim_nao("Apresentou atraso para andar?", "anam_andar", info_adicional=True, label_adicional="Idade com que andou:")

    st.subheader("3. Aspectos Auditivos e Alimentares")
    resp_aud, det_aud = pergunta_sim_nao("Dificuldade para ouvir ou atentar-se a sons?", "anam_aud")
    resp_mast, det_mast = pergunta_sim_nao("Dificuldade ou recusa na mastigação/deglutição?", "anam_mast", info_adicional=True, label_adicional="Descreva os alimentos recusados:")

    st.markdown("---")
    if st.button("💾 Gravar e Consolidar Triagem Inicial", key="btn_salvar_anamnese"):
        st.success(f"✅ Triagem de {paciente_anamnese} consolidada com sucesso no simulador!")

# =====================================================================
# ABA 5: CENTRAL DO PACIENTE (PRONTUÁRIO INTELIGENTE - INFANTIL & ADULTO)
# =====================================================================
with aba5:
    st.header("🗂️ Central do Paciente & Evolução Clínica")
    st.write("Prontuário ágil adaptado para fluxos infantis (TEA/Atrasos) e adultos (Disfagia/Afasia).")

    lista_pacientes_prontuario = ["Arthur Silva (Infantil - TEA)", "Beatriz Souza (Infantil - Apraxia)", "Carlos Eduardo (Adulto - Pós-AVC)"]
    paciente_atual = st.selectbox("Selecione o Prontuário Ativo:", lista_pacientes_prontuario, key="prontuario_p_sel")
    
    # Sub-abas internas para organizar o fluxo clínico sem poluir a tela
    sub_aba_infantil, sub_aba_adulto, sub_aba_midia = st.tabs([
        "👶 Fluxo Infantil & PEI", 
        "🧓 Fluxo Adulto/Idoso", 
        "🎥 Anexos Multimídia & Treinos"
    ])

    # --- 1. FLUXO INFANTIL (Evolução por Tags e PEI) ---
    with sub_aba_infantil:
        st.subheader("🎯 Plano de Ensino Individualizado (PEI) & Metas")
        
        with st.expander("📊 Definir/Visualizar Metas do PEI (Trimestral)", expanded=True):
            col_pei1, col_pei2 = st.columns(2)
            with col_pei1:
                st.markdown("**Meta 1 (Linguagem Expressiva):** Produzir fonemas /r/ intercalados.")
                st.select_slider("Progresso Meta 1:", options=["Não Iniciado", "Em Introdução", "Com Apoio", "Independente"], value="Com Apoio", key="pei_m1")
            with col_pei2:
                st.markdown("**Meta 2 (Comportamental/Socioemocional):** Manter contato visual por 3s.")
                st.select_slider("Progresso Meta 2:", options=["Não Iniciado", "Em Introdução", "Com Apoio", "Independente"], value="Em Introdução", key="pei_m2")

        st.markdown("---")
        st.subheader("⚡ Evolução Ágil por Cliques (Sem Digitação)")
        st.caption("Marque o desempenho da criança durante a atividade lúdica:")
        
        col_t1, col_t2, col_t3, col_t4 = st.columns(4)
        if col_t1.button("🎯 Alvo Atingido", use_container_width=True, type="primary", key="btn_alvo"):
            st.toast("Adicionado: Alvo atingido com sucesso!", icon="🎯")
        if col_t2.button("👁️ Produção c/ Apoio Visual", use_container_width=True, key="btn_ap_visual"):
            st.toast("Adicionado: Production correta com apoio visual", icon="👁️")
        if col_t3.button("🔄 Produção c/ Apoio Verbal", use_container_width=True, key="btn_ap_verbal"):
            st.toast("Adicionado: Produção com apoio verbal", icon="🔄")
        if col_t4.button("⚠️ Recusa / Choro", use_container_width=True, key="btn_recusa"):
            st.toast("Adicionado: Recusa da atividade", icon="⚠️")

        col_ev1, col_ev2 = st.columns(2)
        with col_ev1:
            st.selectbox("Nível de Atenção/Engajamento:", ["Adequado", "Baixo", "Excelente"], key="sel_atencao")
            st.multiselect("Recursos Lúdicos Utilizados:", ["Jogo de Tabuleiro", "Livro Infantil", "Brinquedo Simbólico", "Espelho", "Massa de Modelar"], key="multi_recursos")
        with col_ev2:
            st.selectbox("Conduta para próxima sessão:", ["Manter Conduta Condizente", "Aumentar Nível de Desafio", "Trocar Estímulo Visual", "Conversar com os Pais"], key="sel_conduta")
            st.text_input("Nota rápida (opcional):", placeholder="Ex: Chorou no início, mas regulou.", key="txt_nota_rapida")

        if st.button("💾 Consolidar Evolução Infantil", key="btn_salvar_ev_infantil"):
            st.success(f"✅ Prontuário de {paciente_atual} atualizado no simulador!")

    # --- 2. FLUXO ADULTO/IDOSO (Disfagia, Afasia e Voz) ---
    with sub_aba_adulto:
        st.subheader("📋 Triagem Estruturada para Adultos")
        
        with st.expander("👅 Motricidade Orofacial & Voz", expanded=False):
            st.radio("Simetria Facial em Repouso:", ["Simétrico", "Assimetria Suave", "Assimetria Severa (Paralisia)"], horizontal=True, key="rad_simetria")
            st.radio("Qualidade Vocal Predominante:", ["Adequada", "Soprosa", "Rouca/Aspera", "Trêmula (Neurológica)"], horizontal=True, key="rad_voz")
            
        with st.expander("🍽️ Gerenciamento de Risco para Disfagia (Deglutição)", expanded=True):
            col_dis1, col_dis2 = st.columns(2)
            with col_dis1:
                st.checkbox("Sinais de Penetração/Aspiração (Tosse/Engasgo com Líquidos)", key="chk_tosse")
                st.checkbox("Voz Molhada após Deglutição", key="chk_voz_molhada")
            with col_dis2:
                st.checkbox("Escape de Alimento por Lábios", key="chk_escape")
                st.checkbox("Resíduo Alimentar em Cavidade Oral (Estase)", key="chk_estase")
            st.select_slider("Consistência Segura Testada:", options=["Zero (Líquidos Finos)", "Nível 1 (Líquidos Pouco Espessos)", "Nível 4 (Pastoso)", "Nível 7 (Alimentos Sólidos)"], key="slide_consistencia")

        with st.expander("🗣️ Avaliação de Linguagem (Afasia / Cognição)", expanded=False):
            st.checkbox("Compreensão verbal preservada para ordens complexas", key="chk_compreensao")
            st.checkbox("Presença de Anomia (Dificuldade de encontrar palavras)", key="chk_anomia")
            st.checkbox("Presença de Parafasias (Troca de palavras/sons)", key="chk_parafasias")
            
        if st.button("💾 Consolidar Evolução Adulto", key="btn_salvar_ev_adulto"):
            st.success(f"✅ Avaliação de {paciente_atual} gravada com sucesso!")

    # --- 3. ANEXO MULTIMÍDIA E COMPARTILHAMENTO DE TREINOS ---
    with sub_aba_midia:
        st.subheader("🎥 Evidências Multimídia do Paciente")
        st.caption("Suba áudios ou vídeos curtos para documentar o avanço fonológico e de fala.")
        st.file_uploader("Selecionar Arquivo de Áudio ou Vídeo (.mp3, .wav, .mp4):", type=["mp3", "wav", "mp4"], key="uploader_midia")
        
        st.markdown("---")
        st.subheader("📲 Compartilhamento de Exercícios Domiciliares")
        st.write("Selecione o treino que o paciente ou cuidador deverá realizar em casa:")
        
        treino_opcao = st.selectbox("Escolha o Modelo de Treino:", [
            "Exercício de Sopro e Vedamento Labial (Infantil)",
            "Higiene Vocal e Hidratação das Pregas Vocais (Adulto)",
            "Manobra de Deglutição Segura / Queixo para Baixo (Disfagia)",
            "Treino de Nomeação de Figuras com Apoio Contextual (Afasia)"
        ], key="sel_treino")
        
        link_simulado_exercicio = "https://fonoclinic-treinos.com"
        texto_whatsapp = f"Olá! Segue o treino de Fonoaudiologia para fazer em casa:\n\n*Treino:* {treino_opcao}\n*Link:* {link_simulado_exercicio}"
        
        st.text_area("Mensagem Formatada para o WhatsApp:", value=texto_whatsapp, height=120, key="txt_whatsapp")
        
        phone_exemplo = "5500999999999"
        link_zap = f"https://whatsapp.com{phone_exemplo}&text={io.BytesIO(texto_whatsapp.encode('utf-8')).getvalue().decode('utf-8')}"
        st.page_link(link_zap, label="🚀 Enviar Treino Direto para o WhatsApp do Paciente", icon="💬")

# =====================================================================
# ABA 6: LAUDOS & EXPORTAÇÕES PDF (MODO DEMO VISUAL)
# =====================================================================
with aba6:
    st.header("📄 Central de Emissão de Laudos, Relatórios & Declarações")
    st.write("Ferramenta para compilar dados da anamnese e do prontuário em arquivos oficiais.")

    paciente_laudo = st.selectbox("Selecione o Paciente para Emitir Documento:", ["Arthur Silva (Infantil - TEA)", "Beatriz Souza (Infantil - Apraxia)", "Carlos Eduardo (Adulto - Pós-AVC)"], key="laudos_p_sel")
    tipo_documento = st.selectbox("Tipo de Documento Oficial:", ["Laudo de Avaliação Fonoaudiológica", "Relatório de Evolução Clínica", "Declaração de Comparecimento", "Encaminhamento para Especialista"])
    
    st.subheader("Conteúdo e Conclusão do Documento")
    texto_laudo = st.text_area("Parecer fonoaudiológico descritivo:", placeholder="Escreva a conclusão diagnóstica e a conduta terapêutica indicada...", key="txt_laudo_desc")

    if st.button("⚙️ Compilar Documento Oficial (PDF)", key="btn_compilar_laudo"):
        if texto_laudo:
            st.success("Documento estruturado compilado com sucesso no simulador local!")
            pdf_buf = io.BytesIO()
            pdf_buf.write(b"Documento Oficial Emitido por FonoClinic Demo v1.5")
            st.download_button("📥 Baixar Documento PDF", data=pdf_buf.getvalue(), file_name=f"documento_{paciente_laudo.replace(' ', '_')}.pdf", mime="application/pdf")
        else:
            st.warning("⚠️ Insira o parecer descritivo para simular a geração do PDF.")

# =====================================================================
# ABA 7: ANAMNESE COMPLETA E ROBUSTA (HISTÓRICO CLÍNICO DETALHADO)
# =====================================================================
with aba7:
    st.header("📚 Anamnese Clínica Completa & Histórico de Desenvolvimento")
    st.write("Questionário detalhado para investigações profundas e primeiro contato clínico estruturado.")

    paciente_anamnese_robusta = st.selectbox(
        "Vincular Histórico ao Paciente:", 
        ["Arthur Silva (Infantil - TEA)", "Beatriz Souza (Infantil - Apraxia)", "Carlos Eduardo (Adulto - Pós-AVC)"], 
        key="anamnese_robusta_p_sel"
    )

    # Divisão por Blocos de Investigação Clínica
    aba_hist_familiar, aba_desenv_global, aba_comportamento = st.tabs([
        "🧬 Histórico Familiar e Gestacional", 
        "🏃 Desenvolvimento Motor e Linguagem Profundo", 
        "🧠 Rotina, Sono e Comportamento"
    ])

    # --- 1. HISTÓRICO FAMILIAR E GESTACIONAL ---
    with aba_hist_familiar:
        st.subheader("Antecedentes Familiares e Período Gestacional")
        
        st.text_area("Casos de alterações de fala, audição ou aprendizagem na família?", 
                     placeholder="Especifique o grau de parentesco e a alteração...", key="rob_fam_antecedentes")
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.radio("Intercorrências durante a gestação (Doenças, quedas, estresse severo)?", ["", "Sim", "Não"], key="rob_gest_intercorrencia")
            st.text_input("Medicamentos utilizados na gestação:", key="rob_gest_med")
        with col_g2:
            st.radio("Tipo de parto:", ["", "Normal / Vaginal", "Cesariana"], key="rob_gest_parto")
            st.text_input("Idade gestacional no nascimento (Semanas):", placeholder="Ex: 38 semanas", key="rob_gest_idade")

        st.markdown("---")
        col_n1, col_n2 = st.columns(2)
        with col_n1:
            st.text_input("Peso ao nascer (Gramas):", placeholder="Ex: 3150g", key="rob_nascer_peso")
            st.radio("Chorou logo ao nascer?", ["", "Sim", "Não"], key="rob_nascer_choro")
        with col_n2:
            st.text_input("Índice de APGAR (se souber):", placeholder="Ex: 9/10", key="rob_nascer_apgar")
            st.radio("Necessitou de UTI neonatal ou oxigênio?", ["", "Sim", "Não"], key="rob_nascer_uti")

    # --- 2. DESENVOLVIMENTO MOTOR E LINGUAGEM PROFUNDO ---
    with aba_desenv_global:
        st.subheader("Marcos do Desenvolvimento e Evolução da Fala")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            st.text_input("Idade em que sustentou a cabeça:", key="rob_mot_cabeca")
            st.text_input("Idade em que sentou sozinho(a):", key="rob_mot_sentou")
            st.text_input("Idade em que começou a engatinhar:", key="rob_mot_engatinhou")
        with col_m2:
            st.radio("Apresenta quedas frequentes ou falta de equilíbrio?", ["", "Sim", "Não"], key="rob_mot_equilibrio")
            st.radio("Usa ou um dia usou chupeta / mamadeira? Até que idade?", ["", "Sim", "Não"], key="rob_mot_bico")
            st.text_input("Idade do desmame e introdução de pastosos:", key="rob_mot_desmame")

        st.markdown("---")
        st.subheader("Aspectos da Comunicação Atual")
        col_l1, col_l2 = st.columns(2)
        with col_l1:
            st.radio("Como se comunica preferencialmente?", ["Gestos", "Sons isolados", "Palavras soltas", "Frases completas"], key="rob_ling_pref")
            st.radio("Atende prontamente quando chamado pelo nome?", ["", "Sim", "Não"], key="rob_ling_nome")
        with col_l2:
            st.radio("Mantém contato visual recíproco durante o diálogo?", ["", "Sim", "Não"], key="rob_ling_olhar")
            st.text_area("Descreva como reage quando não é compreendido(a):", placeholder="Ex: Aponta, chora, desiste, morde...", key="rob_ling_frustracao")

    # --- 3. ROTINA, SONO E COMPORTAMENTO ---
    with aba_comportamento:
        st.subheader("Rotina Diária e Comportamento Social")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.radio("Qualidade do sono da criança/paciente:", ["Tranquilo", "Agitado", "Acorda várias vezes", "Terror noturno"], key="rob_sono_qualidade")
            st.radio("Dorme sozinho(a) no próprio quarto?", ["", "Sim", "Não"], key="rob_sono_quarto")
        with col_s2:
            st.radio("Exposição diária a telas (TV, celular, tablet):", ["Não exposto", "Menos de 1 hora", "De 1 a 3 horas", "Mais de 3 horas"], key="rob_comport_telas")
            st.text_input("Quais os brinquedos ou themes de maior interesse (Hiperfoco)?", key="rob_comport_foco")

        st.markdown("---")
        st.subheader("Socialização e Escolaridade")
        st.radio("Frequenta a escola/creche?", ["", "Sim", "Não"], key="rob_esc_frequenta")
        st.text_input("Série atual e comportamento relatado pela professora:", key="rob_esc_relato")
        st.text_area("Como interage com outras crianças da mesma idade?", placeholder="Ex: Brinca junto, brinca isolado, divide brinquedos...", key="rob_esc_interacao")

        st.markdown("---")
        if st.button("💾 Arquivar Anamnese Robusta no Prontuário", key="btn_salvar_anamnese_robusta"):
            st.success(f"🎉 Perfeito! O histórico detalhado de {paciente_anamnese_robusta} foi compilado e estruturado com sucesso no simulador!")
