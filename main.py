import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


def importar_csv_osciloscopio(arquivo: str) -> pd.DataFrame:
    """
    Importa um arquivo CSV gerado pelo Osciloscópio e retorna um DataFrame do pandas.

    Parâmetros:
    arquivo (str): Caminho para o arquivo CSV a ser importado.

    Retorna:
    pd.DataFrame: DataFrame contendo os dados do arquivo CSV.
    """
    try:
        df = pd.read_csv(arquivo, sep=";", decimal=",")
        infos = df[df.columns[0:2]]
        df = df.drop(columns=df.columns[0:3])
        df.columns = ["tempo", "tensao"]
        infos.dropna(inplace=True)
        infos.columns = ["parametro", "valor"]

        return df
    except Exception as e:
        print(f"Erro ao importar o arquivo: {e}")
        return pd.DataFrame()


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


def main():
    figura, ax = plt.subplots(2, 1, figsize=(10, 8))

    arquivo = "dados/V1.txt"
    df1 = importar_csv_simulador(arquivo)
    df1.plot(x="tempo", y="tensao", xlabel="Tempo (s)", ylabel="Tensão (V)", style=":*r", ax=ax[0], label="Simulador")

    arquivo = "dados/Osciloscópio - F0000CH2.csv"
    df2 = importar_csv_osciloscopio(arquivo)

    df2.plot(x="tempo", y="tensao", xlabel="Tempo (s)", ylabel="Tensão (V)", style=":b", ax=ax[0], label="Osciloscópio")

    ax[0].set_xlim(-0.1, 2)

    tempo = np.arange(0, 2, 0.01)
    tensao = 1 - 0.993 * np.exp(-tempo * 4.51) - 0.0063 * np.exp(-tempo * 10.08)
    ax[0].plot(tempo, tensao, ":+g", label="Analítico")

    ax[0].set_title("Comparação entre Simulador e Osciloscópio para $V_1(t)$")
    ax[0].legend()

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

    plt.show()


if __name__ == "__main__":
    main()
