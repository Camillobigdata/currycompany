# libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import re
import streamlit as st
import datetime
import folium
from streamlit_folium import folium_static

from PIL import Image # aqui importamos a biblioteca para colocar imagens no streamlit


st.set_page_config(page_title='Visão Entregadores', layout='wide')

# ---------------------------------------
# Funções
# ---------------------------------------
def top_delivers(df1, top_asc):
    df2 = df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']].groupby(['City', 'Time_taken(min)']).mean().sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index() 
    
    df_aux01 = df2.loc[df2['City']  == 'Metropolitian ', :].head(10)
    df_aux02 = df2.loc[df2['City']  == 'Urban ', :].head(10)
    df_aux03 = df2.loc[df2['City']  == 'Semi-Urban ', :].head(10)
    
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)
    
    return df3
        
def clean_code(df):
    """ Esta função tem a responsabilibsade de limpar o dataframe
    
        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo de coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica)

        Imput: dataframe
        Output: dataframe
    """
    # Remover spaco da string
    df['ID'] = df['ID'].str.strip()
    df['Delivery_person_ID'] = df['Delivery_person_ID'].str.strip()
    
    # Excluir as linhas com a idade dos entregadores vazia
    # ( Conceitos de seleção condicional )
    linhas_vazias = df['Delivery_person_Age'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['Road_traffic_density'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['City'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    linhas_vazias = df['Festival'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    
    # Conversao de texto/categoria/string para numeros inteiros
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )
    
    # Conversao de texto/categoria/strings para numeros decimais
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )
    
    # Conversao de texto para data
    df['Order_Date'] = pd.to_datetime( df['Order_Date'], format='%d-%m-%Y' )
    
    # Remove as linhas da culuna multiple_deliveries que tenham o
    # conteudo igual a 'NaN '
    linhas_vazias = df['multiple_deliveries'] != 'NaN '
    df = df.loc[linhas_vazias, :]
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )
    
    # Comando para remover o texto de números
    df = df.reset_index( drop=True )
    
    # Retirando os numeros da coluna Time_taken(min)
    df['Time_taken(min)'] = df['Time_taken(min)'].str.extract(r'(\d+)').fillna('0').astype(int)
    
    # Retirando os espaços da coluna Festival
    df['Festival'] = df['Festival'].str.strip()

    return df
# -------------------------------- 
# Inicio da Estrutura 
# -------------------------------

# ---------------------------------------
# Lendo e copiando DataFrame
# ---------------------------------------

df_raw = pd. read_csv('dataset/train.csv')
df = df_raw.copy()

# --------------------------------------
# Limpando o dataframe
# --------------------------------------
df = clean_code(df)

# -------------------------------------
# Copia do df
# -------------------------------------

df1 = df.copy()

# -------------------------------------
# Barra Lateral
# -------------------------------------

st.header( "Market Place - Visão Entregadores")

st.sidebar.markdown('# Cury Comapny')
st.sidebar.markdown('## Fastest delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime.datetime(2022, 4, 13),
    min_value=datetime.datetime(2022, 2, 11), #mudou o datetime, agora é necessário importar o datetime
    max_value=datetime.datetime(2022, 4, 6),
    format='DD-MM-YYYY')
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições de Transito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown("""---""")

# Filtro de Data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# Filtro de Transito
#linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
#df1 = df1.loc[linhas_selecionadas, :]

# ----------------------------------------
# Layout no Streamlit
# ----------------------------------------

tab1, tab2, tab3 = st.tabs(['Visão geral', '', ''])

with tab1:

    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Maior Idade
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior de idade', maior_idade)


        with col2:
            # menor idade
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor de idade', menor_idade)


        with col3:
            # Melhor condição
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('A Melhor condição', melhor_condicao)


        with col4:
            # Pior Condição
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('A Pior condição', pior_condicao)


    with st.container():
        st.markdown("""___""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)


    with col1:
        st.subheader('Avaliações média por entregador')
        df_avg_ratings_per_deliver = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                        .groupby('Delivery_person_ID')
                                        .mean()
                                        .reset_index())
        st.dataframe(df_avg_ratings_per_deliver)


    with col2:
        with st.container():
            st.subheader('Avalicacões média por trânsito')
            df_avg_std_rating_by_traffic = ( df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density',] ]
                                                .groupby('Road_traffic_density')
                                                .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            # Mudança de nome das colunas
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']

            # reset do index
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()

            st.dataframe(df_avg_std_rating_by_traffic)

        with st.container():
            st.subheader('Avalicacões média por clima')
            df_avg_std_rating_by_weather = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions',] ]
                                                .groupby('Weatherconditions')
                                                .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            # Mudança de nome das colunas
            df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']

            # reset do index
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()

            st.dataframe(df_avg_std_rating_by_weather)
            



    with st.container():
        st.markdown("""___""")
        st.title('Velocidade de Entrega')
        col1, col2 = st.columns(2)

    with col1:
        st.subheader('Top entregadores mais rápidos')
        df3 = top_delivers(df1, top_asc=True)
        st.dataframe(df3)
        

    with col2:
        st.subheader('Top entregadores mais lentos')
        df3 = top_delivers(df1, top_asc=False)
        st.dataframe(df3)

        
    