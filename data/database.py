#-----------------------------------------------------------------------------#
# Módulo de conexão ao banco de dados                                         #
# Por: Pedro T. R. Pinheiro         21/MAR/2018                               #
#-----------------------------------------------------------------------------#

from os import environ as env
import psycopg2 as psql

SQLPARAMS = "host=localhost dbname=mercurium user=mercurium password=" + env['DBKEY']

def dbConnect():
    '''
    :return: Um objeto representando a conexão PSQL, ou uma string, em caso de erro
    '''
    try:
        conn = psql.connect(SQLPARAMS)
    except psql.Error as e:
        conn = e

    return conn

def execNonQuery():
    '''
    Executa uma operação da qual não se espera saída significativa
    :return:
    '''

    conn = dbConnect()

    ### Este arquivo será responsável pelos métodos que lidam diretamente com a base de dados
    ### Mas aí que tá: não decidi nem se vai usar banco e tampouco se será com stored procedures!
    ### Só tô dando commit para evitar B.O.s futuros.