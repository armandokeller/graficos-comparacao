# Como gerar gráficos com Matplotlib a partir de dados em CSV e equações matemáticas

O objetivo deste guia é demonstrar como gerar gráficos utilizando dados reais obtidos de experimentos ou simuladores, armazenados em arquivos CSV, e também como plotar gráficos a partir de equações matemáticas usando a biblioteca Matplotlib em Python. Desta forma, é possível comparar visualmente os dados experimentais com as previsões teóricas.

## Pré-requisitos
Antes de começar, você precisará ter o Python instalado em sua máquina (ou outro ambiente de desenvolvimento como o [google colab](https://colab.research.google.com/)), assim como as bibliotecas necessárias. Você pode instalar as bibliotecas necessárias usando o gerenciador de pacotes `pip`. Execute o seguinte comando:

```bash
pip install matplotlib pandas numpy
```
Uma boa prática para gerenciar as bibliotecas é utilizar um ambiente virtual para cada projeto. Um dos gerenciadores mais modernos é o [UV](https://docs.astral.sh/uv/getting-started/installation/) o qual foi utilizado para criar este projeto. Uma vez instalado o UV, o ambiente virtual pode ser criado com o comando:

```bash
uv sync
```
Este comando cria um ambiente virtual e instala todas as dependências listadas no arquivo `pyproject.toml`. O ambiente virtual ficará armazenado na pasta `.venv` do projeto. 

As bibliotecas que serão utilizadas neste guia são:
- [matplotlib](https://matplotlib.org/): para criação de gráficos.
- [pandas](https://pandas.pydata.org/): para manipulação e análise de dados, especialmente para ler arquivos CSV.
- [numpy](https://numpy.org/): para operações matemáticas e manipulação de arrays.

Os arquivos CSV utilizados neste guia estão armazenados na pasta `dados`. Você pode baixar os arquivos diretamente do repositório ou criar seus próprios arquivos CSV com dados experimentais.

## Iniciando o código
A primeira etapa do código é importar as bibliotecas necessárias. É recomendado importar as bibliotecas com seus apelidos convencionais para facilitar o uso ao longo do código.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
```



## Entendendo os dados

Antes de começar a desenvolver o código é importante entender os dados e a estrutura dos arquivos CSV. Neste guia, utilizaremos dois arquivos CSV como exemplo:
- `dados/Osciloscópio - F0000CH1.CSV`: que contém os dados de um canal do osciloscópio (tempo e tensão).
- `dados/V1.CSV`: que contém os dados da simulação do LT Spice (tempo e tensão).

### Arquivo do osciloscópio
As primeiras linhas do arquivo `Osciloscópio - F0000CH1.CSV` permitirão entender a estrutura dos dados. As primeiras linhas do arquivo são:

```
Record Length;2,50E+03;;-0,12;0
Sample Interval;1,00E-03;;-0,119;0
Trigger Point;1,20E+02;;-0,118;0
;;;-0,117;0
;;;-0,116;0
;;;-0,115;0
Source;CH1;;-0,114;0
Vertical Units;V;;-0,113;0
Vertical Scale;5,00E-02;;-0,112;0
Vertical Offset;-1,80E-01;;-0,111;-0,01
Horizontal Units;s;;-0,11;0
Horizontal Scale;2,50E-01;;-0,109;-0,002
Pt Fmt;Y;;-0,108;0
Yzero;0,00E+00;;-0,107;0
Probe Atten;1,00E+00;;-0,106;0
Model Number;TBS1052B-EDU;;-0,105;0
Serial Number;C012440;;-0,104;0
Firmware Version;FV:v4.0;;-0,103;0
;;;-0,102;0
;;;-0,101;0
;;;-0,1;0
```


Destes dados é possível perceber que o separador das colunas é o ponto e vírgula (`;`) e que as vírgulas (`,`) são utilizadas para separar os decimais. As primeiras colunas representam informações referentes aos parâmetros do osciloscópio no momento da captura dos dados. As duas últimas colunas representam os dados de tempo (em segundos) e tensão (em volts) respectivamente. 

Uma vez que que o formato do arquivo foi compreendido, vamos criar uma função para ler os dados do arquivo e retornar um DataFrame do Pandas com os dados de tempo e tensão.

```python
def importar_csv_osciloscopio(arquivo: str) -> pd.DataFrame:
    """
    Importa um arquivo CSV gerado pelo Osciloscópio e retorna um DataFrame do pandas.

    Parâmetros:
    arquivo (str): Caminho para o arquivo CSV a ser importado.

    Retorna:
    pd.DataFrame: DataFrame contendo os dados do arquivo CSV.
    """
    try:
        df = pd.read_csv(arquivo, sep=";", decimal=",")     # Lê o arquivo CSV com o separador e decimal corretos
        infos = df[df.columns[0:2]]                         # Seleciona as primeiras duas colunas com informações do osciloscópio
        df = df.drop(columns=df.columns[0:3])               # Remove as primeiras três colunas, mantendo apenas os dados de tempo e tensão
        df.columns = ["tempo", "tensao"]                    # Renomeia as colunas para "tempo" e "tensao"
        infos.dropna(inplace=True)                          # Remove linhas com valores NaN (vazios)
        infos.columns = ["parametro", "valor"]              # Renomeia as colunas de informações
        return df                                           # Retorna o DataFrame com os dados de tempo e tensão
    except Exception as e:
        # Caso ocorra algum erro na importação, exibe uma mensagem de erro e retorna um DataFrame vazio
        print(f"Erro ao importar o arquivo: {e}")
        return pd.DataFrame()

```
Neste caso os valores já estavam com a escala correta aplicada, mas caso fosse necessário aplicar alguma escala isto poderia ser feito  antes de retornar o DataFrame. Por exemplo, para obter a escala vertical e horizontal e aplicar aos dados:

```python
        escala_vertical = float(infos.query("parametro == 'Vertical Scale'")['valor'].values[0].replace(',', '.'))
        escala_horizontal = float(infos.query("parametro == 'Horizontal Scale'")['valor'].values[0].replace(',', '.'))
        df['tensao'] *= escala_vertical 
        df['tempo'] *= escala_horizontal
```

### Arquivo do LT Spice
As primeiras linhas do arquivo `V1.CSV` permitirão entender a estrutura dos dados. As primeiras linhas do arquivo são:

```
time	V(n002)
0,00E+00	0,00E+00
1,00E-09	4,55E-09
2,00E-09	9,09E-09
2,81E-03	1,27E-02
5,62E-03	2,52E-02
8,43E-03	3,76E-02
1,12E-02	4,98E-02
```
Neste caso o separador das colunas é a tabulação (`\t`) e as vírgulas (`,`) são utilizadas para separar os decimais. A primeira linha representa o cabeçalho com os nomes das colunas. A primeira coluna representa os dados de tempo (em segundos) e a segunda coluna representa os dados de tensão (em Volts).

Uma vez que que o formato do arquivo foi compreendido, vamos criar uma função para ler os dados do arquivo e retornar um DataFrame do Pandas com os dados de tempo e tensão.

```python
def importar_csv_simulador(arquivo: str) -> pd.DataFrame:
    """
    Importa um arquivo CSV gerado pelo Simulador de Investimentos e retorna um DataFrame do pandas.

    Parâmetros:
    arquivo (str): Caminho para o arquivo CSV a ser importado.

    Retorna:
    pd.DataFrame: DataFrame contendo os dados do arquivo CSV.
    """
    try:
        df = pd.read_csv(arquivo, sep="\t", decimal=",")
        df.columns = ["tempo", "tensao"]
        # o parâmetro sep='\t' define o separador de campos como tabulação
        # o parâmetro decimal=',' define o separador decimal como vírgula (convertendo para ponto)
        return df
    except Exception as e:
        print(f"Erro ao importar o arquivo: {e}")
        return pd.DataFrame()
```

## Plotando os dados

Agora que as funções para importar os dados dos arquivos CSV foram criadas, podemos utilizá-las para ler os dados e plotá-los utilizando o Matplotlib. Para que o código fique mais organizado, vamos encapsular o código que lê os arquivos e plota os gráficos em uma função principal chamada `main`.

```python
def main()->None:
    ...
```

Dentro da função main, vamos criar a nossa figura e os eixos do gráfico utilizando o Matplotlib. Vamos definir o tamanho da figura para que fique mais legível.

```python
    figura, ax = plt.subplots(2, 1, figsize=(10, 8)) 
```
O comando `plt.subplots(2, 1)` cria uma figura com dois gráficos empilhados verticalmente (2 linhas e 1 coluna). O parâmetro `figsize=(10, 8)` define o tamanho da figura em polegadas. [Documentação do Matplotlib](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.subplots.html).


```python
    # Importa o arquivo do simulador para o primeiro gráfico (ax[0])
    arquivo = "dados/V1.txt"                             
    df1 = importar_csv_simulador(arquivo)
    df1.plot(x="tempo", y="tensao", xlabel="Tempo (s)", ylabel="Tensão (V)", style=":*r", ax=ax[0], label="Simulador")

    # Importa o arquivo do osciloscópio para o primeiro gráfico (ax[0])
    arquivo = "dados/Osciloscópio - F0000CH2.csv"
    df2 = importar_csv_osciloscopio(arquivo)
    df2.plot(x="tempo", y="tensao", xlabel="Tempo (s)", ylabel="Tensão (V)", style=":b", ax=ax[0], label="Osciloscópio")

    # Define os limites do eixo x para o primeiro gráfico
    ax[0].set_xlim(-0.1, 2)
```

Agora para os dados analíticos (calculados), vamos utilizar a biblioteca NumPy para criar um array de valores de tensão em função do tempo. Primeiro precisamos dos dados do tempo, que neste caso podemos aproveitar os dados do CSV do simulador ou criar um novo array.
Para o primeiro sinal vamos utilizar a expressão matemática $v_1(t) = 1 - 0,993 e^{-4,51t} - 0,0063 e^{-10,08t}$.

```python
    tempo = np.arange(0, 2, 0.01)                                                   # Cria um array de valores de tempo de 0 a 2 segundos com passo de 0.01 segundos
    tensao = 1 - 0.993 * np.exp(-tempo * 4.51) - 0.0063 * np.exp(-tempo * 10.08)    # Calcula os valores de tensão usando a expressão matemática
    ax[0].plot(tempo, tensao, ":+g", label="Analítico")                             # Plota os dados analíticos no primeiro gráfico

    ax[0].set_title("Comparação entre Simulador e Osciloscópio para $V_1(t)$")      # Define o título do primeiro gráfico
    ax[0].legend()                                                                  # Adiciona a legenda ao primeiro gráfico
``` 

Agora repetimos o processo para o segundo gráfico (ax[1]). Neste caso, para o segundo sinal vamos utilizar a expressão matemática $v_2(t) = 0,8159 (e^{-4,51t} - e^{-10,08t})$.

```python
    arquivo = "dados/V2.txt"
    df1 = importar_csv_simulador(arquivo)
    df1.plot(x="tempo", y="tensao", xlabel="Tempo (s)", ylabel="Tensão (V)", style=":*r", ax=ax[1], label="Simulador")

    arquivo = "dados/Osciloscópio - F0000CH1.csv"
    df2 = importar_csv_osciloscopio(arquivo)

    df2.plot(x="tempo", y="tensao", xlabel="Tempo (s)", ylabel="Tensão (V)", style=":b", ax=ax[1], label="Osciloscópio")

    ax[1].set_xlim(-0.1, 2)

    tempo = np.arange(0, 2, 0.01)
    tensao = 0.8159 * (np.exp(-tempo * 4.51) - np.exp(-tempo * 10.08))
    ax[1].plot(tempo, tensao, ":+g", label="Analítico")

    ax[1].set_title("Comparação entre Simulador e Osciloscópio para $V_2(t)$")
    ax[1].legend()

    plt.show()    # Exibe os gráficos
```

Com isto a função main está completa. Agora só falta chamar a função main quando o script for executado diretamente.

```python
if __name__ == "__main__":
    main()
```

O código completo está disponível no arquivo [main.py](/main.py).

Um exemplo do gráfico gerado pode ser visto abaixo:
![Exemplo de gráfico gerado](/imagens/exemplo.png)

## Melhorias
Este guia apresentou uma introdução básica sobre como gerar gráficos utilizando dados de arquivos CSV e equações matemáticas com Matplotlib. Algumas melhorias ainda podem ser feitas, como questões de estilo, cores, tipos de gráficos, entre outros. Além de poder utilizar os dados para realizar análises estatísticas, como média, mediana, desvio padrão, entre outros.

Algumas sugestões de melhorias incluem:
 - **Anotações de informações importantes no gráfico:** Para destacar pontos a serem analisados é possível adicionar anotações no gráfico utilizando a função `annotate` do Matplotlib. [Documentação sobre anotações no Matplotlib](https://matplotlib.org/stable/users/explain/text/annotations.html#annotations)


- **Diferentes estilos de linhas e marcadores:** O Matplotlib oferece uma variedade de estilos de linhas e marcadores que podem ser utilizados para melhorar a aparência dos gráficos. [Documentação sobre estilos de linhas e marcadores](https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.plot.html#matplotlib.pyplot.plot)

- **Utilizar outros estilos de gráficos:** Existem outras bibliotecas que funcionam em conjunto com o Matplotlib para criar gráficos mais avançados como é o caso da Seaborn. [Documentação do Seaborn](https://seaborn.pydata.org/)