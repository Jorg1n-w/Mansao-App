import streamlit as st
import pandas as pd
from supabase import create_client, Client

# Configuração da Página
st.set_page_config(page_title="Mansão App")

if 'grupo_aberto' not in st.session_state:
    st.session_state.grupo_aberto = None
    
if 'selecao_aberta' not in st.session_state:
    st.session_state.selecao_aberta = None

if 'grupo_aberto_repetidas' not in st.session_state:
    st.session_state.grupo_aberto_repetidas = None
    
if 'selecao_aberta_repetidas' not in st.session_state:
    st.session_state.selecao_aberta_repetidas = None

st.markdown("""
    <style>
        /* 1. Otimização do Layout do Streamlit para Celular */
        @media (max-width: 640px) {
            /* Força as colunas a ficarem lado a lado (Grid de 4) */
            div[data-testid="stColumns"],
            div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: wrap !important;
                gap: 2% !important; /* Espaço mínimo entre as colunas */
            }
            
            /* Define que cada coluna ocupa 23.5% (cabem 4 na tela) */
            div[data-testid="stColumn"],
            div[data-testid="column"] {
                width: 23.5% !important;
                flex: 0 0 23.5% !important;
                min-width: 23.5% !important;
                padding: 0 !important; /* Remove o padding da coluna */
                margin-bottom: 6px !important; /* Distância para a linha de baixo */
            }
        }

        /* 2. Estilização Global dos Botões (Formato Figurinha) */
        /* Alvo: Botões que estão dentro das colunas */
        div[data-testid="stColumns"] button {
            height: 45px !important; /* Força uma altura quadrada padrão */
            padding: 0 !important; /* Remove o respiro interno do botão */
            margin: 0 !important; 
            border-radius: 6px !important; /* Bordas levemente arredondadas */
            display: flex !important;
            justify-content: center !important;
            align-items: center !important;
            font-size: 14px !important; /* Tamanho da fonte mais legível */
            font-weight: 600 !important; /* Texto em negrito */
            letter-spacing: 0.5px !important; /* Espaçamento entre as letras */
            transition: all 0.2s ease !important;
            width: 100% !important;
        }

        /* 3. Cores Customizadas (Opcional, para deixar mais bonito) */
        /* Botão Faltante (Secundário) */
        button[data-testid="baseButton-secondary"] {
            background-color: transparent !important;
            border: 1.5px solid #444 !important; /* Borda cinza escura */
            color: #ccc !important;
        }
        
        /* Botão Obtido (Primário) */
        button[data-testid="baseButton-primary"] {
            background-color: #ff4b4b !important; /* Vermelho Streamlit / Copa */
            border: 1.5px solid #ff4b4b !important;
            color: white !important;
        }
            
        .texto-lista {
            display: flex;
            align-items: center;
            height: 45px;
            font-size: 16px;
            font-weight: bold;
        }
        .numero-lista {
            display: flex;
            align-items: center;
            justify-content: center;
            height: 45px;
            font-size: 18px;
            font-weight: bold;
            color: #ff4b4b; /* Vermelho para destacar a quantidade */
        }
    </style>
""", unsafe_allow_html=True)

# Conecta supabase
url = "https://pbgqppburbsifxikmgjy.supabase.co"
key = "sb_publishable_3wX2yAg-4iPKxnujUa_TYA_fqk0SdCN"
supabase: Client = create_client(url, key)

# Popula df com dados do supabase
get = supabase.table('Figurinhas').select("*").execute()
df = pd.DataFrame(get.data)

if not df.empty:
    df = df.sort_values(by='IdFigurinha')

    total_figurinhas = len(df)
    total_obtidas = df['Obtido'].sum()
    # Proteção caso o banco venha zerado para não dar erro de divisão por zero
    obtidas_pct = round((total_obtidas/total_figurinhas)*100) if total_figurinhas > 0 else 0

    st.title(f"Mansão das Figurinhas")
    st.subheader(f"Progresso: {obtidas_pct}% ({total_obtidas}/{total_figurinhas})")
    st.write("Completar o albúm é nossa única meta")

    aba_album, aba_repetidas = st.tabs(["📒 Álbum", "🔁 Repetidas"])

    with aba_album:
        
        item_pesquisa = st.text_input("🔍 Pesquisar figurinha, seleção ou grupo: (figurinhas devem ser pesquisadas pelo código. Ex: KSA01, MEX19. Apague e aperte enter para limpar.)")
        df_filtrado = df.copy()

        if item_pesquisa:
            df_filtrado = df_filtrado[
                df_filtrado['Grupo'].str.contains(item_pesquisa, case=False, na=False) |
                df_filtrado['Selecao'].str.contains(item_pesquisa, case=False, na=False) |
                df_filtrado['Cod_Figurinha'].str.contains(item_pesquisa, case=False, na=False)
            ]

        df = df_filtrado

        if not df.empty:
            distinct_grupos = df['Grupo'].unique()

            # Sanfona 1 (Grupos)
            for grupo in distinct_grupos:
                manter_aberto_grupo = (st.session_state.grupo_aberto == grupo)
                obtido_grupo = df.loc[df['Grupo'] == grupo, 'Obtido'].sum()
                total_grupo = df.loc[df['Grupo'] == grupo, 'Obtido'].count()
                pct_grupo = round((obtido_grupo/total_grupo)*100) if total_grupo > 0 else 0

                with st.expander(f'⚽ Grupo {grupo} | {pct_grupo}% ({obtido_grupo}/{total_grupo})', expanded=manter_aberto_grupo):
                    selecoes_grupo = df[df['Grupo'] == grupo]['Selecao'].unique()

                    # Sanfona 2 (Seleções)
                    for selecao in selecoes_grupo:
                        manter_aberto_selecao = (st.session_state.selecao_aberta == selecao)
                        obtido_selecao = df.loc[df['Selecao'] == selecao, 'Obtido'].sum()
                        total_selecao = df.loc[df['Selecao'] == selecao, 'Obtido'].count()
                        pct_selecao = round((obtido_selecao/total_selecao)*100) if total_selecao > 0 else 0

                        with st.expander(f'👕 {selecao} | {pct_selecao}% ({obtido_selecao}/{total_selecao})', expanded=manter_aberto_selecao):
                            
                            figurinhas_selecao = df[(df['Grupo'] == grupo) & (df['Selecao'] == selecao)]
                            figurinhas_selecao = figurinhas_selecao.sort_values(by='IdFigurinha')

                            colunas = st.columns(4)

                            # Usamos o 'enumerate' para garantir que os botões comecem sempre na primeira coluna (0)
                            for i, (index, linha) in enumerate(figurinhas_selecao.iterrows()):
                                id_fig = linha['IdFigurinha']
                                num_fig = linha['Num_Figurinha']
                                status = linha['Obtido']
                                figurinha = linha['Cod_Figurinha']

                                cor = 'primary' if status else 'secondary'
                                icone = '✅' if status else ''
                                
                                # 'i' vai ser 0, 1, 2, 3, 4... garantindo a ordem perfeita da grade
                                col_atual = i % 4

                                with colunas[col_atual]:
                                    clicou = st.button(
                                        label=f"{figurinha}{icone}",
                                        key=f"btn_{id_fig}",
                                        type=cor,
                                        use_container_width=True
                                    )

                                    if clicou:
                                        novo_status = not status
                                        supabase.table('Figurinhas').update({'Obtido': novo_status}).eq('IdFigurinha', id_fig).execute()

                                        st.session_state.grupo_aberto = grupo
                                        st.session_state.selecao_aberta = selecao
                                        st.rerun()

        else:
            st.info("Nenhuma figurinha encontrada para a busca atual.")
    with aba_repetidas:
        item_pesquisa_REP = st.text_input("🔍 Pesquisar figurinha, seleção ou grupo:  (figurinhas devem ser pesquisadas pelo código. Ex: KSA01, MEX19. Apague e aperte enter para limpar.)")
        df_filtrado = df[df['Obtido'] == True]

        if item_pesquisa_REP:
            df_filtrado = df_filtrado[
                df_filtrado['Grupo'].str.contains(item_pesquisa_REP, case=False, na=False) |
                df_filtrado['Selecao'].str.contains(item_pesquisa_REP, case=False, na=False) |
                df_filtrado['Cod_Figurinha'].str.contains(item_pesquisa_REP, case=False, na=False)
            ]

        df = df_filtrado

        if not df.empty:
            distinct_grupos = df['Grupo'].unique()

            for grupo in distinct_grupos:
                manter_aberto_grupo_repetidas = (st.session_state.grupo_aberto_repetidas == grupo)

                total_repetidas_grupo = df.loc[df['Grupo'] == grupo, 'QTD'].sum()

                with st.expander(f"⚽ Grupo {grupo} | {total_repetidas_grupo} repetidas", expanded=manter_aberto_grupo_repetidas):
                    selecoes_grupo = df[df['Grupo'] == grupo]['Selecao'].unique()

                    for selecao in selecoes_grupo:
                        manter_aberto_selecao_rep = (st.session_state.selecao_aberta_repetidas == selecao)
                        total_rep_selecao = df.loc[df['Selecao'] == selecao, 'QTD'].sum()

                        with st.expander(f'👕 {selecao} | {total_rep_selecao} Repetidas', expanded=manter_aberto_selecao_rep):
                            
                            figurinhas_selecao = df[(df['Grupo'] == grupo) & (df['Selecao'] == selecao)]
                            figurinhas_selecao = figurinhas_selecao.sort_values(by='IdFigurinha')

                            for index, linha in figurinhas_selecao.iterrows():
                                id_fig = linha['IdFigurinha']
                                figurinha = linha['Cod_Figurinha']

                                qtd_repetidas = int(linha['QTD']) if pd.notna(linha['QTD']) else 0

                                #espaço das colunas na tela
                                col_texto, col_menos, col_qtd, col_mais = st.columns([4, 1, 1, 1])

                                with col_texto:
                                    st.markdown(f"<div class='texto-lista'>{figurinha}</div>", unsafe_allow_html=True)
                                
                                with col_menos:
                                    if st.button("➖", key=f"menos_{id_fig}", type="secondary", use_container_width=True):
                                        if qtd_repetidas > 0: # Impede o número de ficar negativo
                                            supabase.table('Figurinhas').update({'QTD': qtd_repetidas - 1}).eq('IdFigurinha', id_fig).execute()
                                            st.session_state.grupo_aberto_rep = grupo
                                            st.session_state.selecao_aberta_rep = selecao
                                            st.rerun()

                                with col_qtd:
                                    st.markdown(f"<div class='numero-lista'>{qtd_repetidas}</div>", unsafe_allow_html=True)
                                
                                with col_mais:
                                    if st.button("➕", key=f"mais_{id_fig}", type="primary", use_container_width=True):
                                        supabase.table('Figurinhas').update({'QTD': qtd_repetidas + 1}).eq('IdFigurinha', id_fig).execute()
                                        st.session_state.grupo_aberto_rep = grupo
                                        st.session_state.selecao_aberta_rep = selecao
                                        st.rerun()
                                        
                                # Cria uma linha divisória quase invisível entre as figurinhas
                                st.markdown("<hr style='margin: 4px 0px; border-color: rgba(255,255,255,0.05);'>", unsafe_allow_html=True)

else:
    st.info("Deu ruim fml! O banco de dados está vazio.")