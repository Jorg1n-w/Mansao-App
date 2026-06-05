
import streamlit as st
import pandas as pd
from supabase import create_client, client

#Configuração da Página
st.set_page_config(page_title="Mansão App")

if 'grupo_aberto' not in st.session_state:
    st.session_state.grupo_aberto = None
    
if 'selecao_aberta' not in st.session_state:
    st.session_state.selecao_aberta = None

st.markdown("""
    <style>
        @media (max-width: 640px) {
            div[data-testid="stHorizontalBlock"] {
                display: flex !important;
                flex-wrap: wrap !important;
            }
            div[data-testid="column"] {
                width: 22% !important;
                flex: 0 0 22% !important;
                min-width: 22% !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

#Conecta supabase
#url = st.secrets["SUPABASE_URL"]
#key = st.secrets["SUPABASE_KEY"]
url = "https://pbgqppburbsifxikmgjy.supabase.co"
key = "sb_publishable_3wX2yAg-4iPKxnujUa_TYA_fqk0SdCN"
supabase: client = create_client(url, key)

#Popula df com dados do supabase
get = supabase.table('Figurinhas').select("*").execute()
df = pd.DataFrame(get.data)
df = df.sort_values(by='IdFigurinha')

total_figurinhas = len(df)
total_obtidas = df['Obtido'].sum()
obtidas_pct = round((total_obtidas/total_figurinhas)*100)

st.title(f"Mansão das Figurinhas")
st.subheader(f"Progresso: {obtidas_pct}% ({total_obtidas}/{total_figurinhas})")
st.write("Completar o albúm é nossa única meta")

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

    #Sanfona1
    for grupo in distinct_grupos:

        manter_aberto_grupo = (st.session_state.grupo_aberto == grupo)
        obtido_grupo = df.loc[df['Grupo'] == grupo, 'Obtido'].sum()
        total_grupo = df.loc[df['Grupo'] == grupo, 'Obtido'].count()
        pct_grupo = round((obtido_grupo/total_grupo)*100)

        with st.expander(f'⚽ Grupo {grupo} | {pct_grupo}% ({obtido_grupo}/{total_grupo})', expanded=manter_aberto_grupo):
            selecoes_grupo = df[df['Grupo'] == grupo]['Selecao'].unique()

            for selecao in selecoes_grupo:

                manter_aberto_selecao = (st.session_state.selecao_aberta == selecao)
                obtido_selecao = df.loc[df['Selecao'] == selecao, 'Obtido'].sum()
                total_selecao = df.loc[df['Selecao'] == selecao, 'Obtido'].count()
                pct_selecao = round((obtido_selecao/total_selecao)*100)

                with st.expander(f'👕 {selecao} | {pct_selecao}% ({obtido_selecao}/{total_selecao})', expanded=manter_aberto_selecao):
                    
                    figurinhas_selecao = df[(df['Grupo'] == grupo) & (df['Selecao'] == selecao)]
                    figurinhas_selecao = figurinhas_selecao.sort_values(by='IdFigurinha')

                    colunas = st.columns(4)

                    for index, linha in figurinhas_selecao.iterrows():
                        id_fig = linha['IdFigurinha']
                        num_fig = linha['Num_Figurinha']
                        status = linha['Obtido']
                        figurinha = linha['Cod_Figurinha']

                        cor = 'primary' if status else 'secondary'
                        icone = '✅' if status else ''
                        
                        col_atual = (id_fig-1) % 4

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
    st.info("deu ruim fml!")