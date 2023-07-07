from array import array
import time
from datetime import datetime, date
from quanser.hardware import HIL, HILError



def aplica_controle(card,sinal_controle: float):
    if (sinal_controle >= 4):
        sinal_controle = 4
    if (sinal_controle <= -4):
        sinal_controle = -4
    sinal_aplicado = sinal_controle
    card.write_digital(array('I', [0]), len(array('I', [0])), array('b', [1])) #Garante que o canal do VoltPAQ vai estar ativo
    card.write_analog(array('I', [0]), len(array('I', [0])), array('d', [sinal_controle]))
    return sinal_aplicado


            
def trava(card,level_1: float, level_2: float, control_signal: float):  #Se o sinal de controle por positivo e atingir o limite máximo, desliga a bomba e para o programa
    #Assim como se o sinal de controle for negativo e atingir o limite mínimo
    print('Trava ativa!')
    if control_signal < 0 and level_2 < -5:
        desligar_bomba(card)
        print('NÍVEL CRÍTICO INFERIOR ATINGIDO - software interrompido por segurança!!!')
        exit()
    if control_signal > 0 and level_2 >= 27:
        desligar_bomba(card)
        print('NÍVEL CRÍTICO SUPERIOR DO TANQUE 2 ATINGIDO - software interrompido por segurança!!!')
        exit()
    if control_signal > 0 and level_1 >= 27:
        desligar_bomba(card)
        print('NÍVEL CRÍTICO SUPERIOR DO TANQUE 1 ATINGIDO - software interrompido por segurança!!!')
        exit()
    
def desligar_bomba(card):
    try:
        aplica_controle(card,0)
        #card.write_analog(array('I', [0]), len(array('I', [0])), array('d', [0]))
    except Exception as e:
        print(e)
        raise

def leia(card):

    #Congiguração das entradas analógicas do módulo Q8-USB
    channels = array('I', [0, 1, 2]) #indica que as entradas 3,6 e 7 do Q8 serão utilizadas (3 e 6 para leitura dos nívels e 7 para a leitura da corrente na bomba
    num_channels = len(channels)
    buffer = array('d', [0.0] * num_channels)

    try:
        card.read_analog(channels, num_channels, buffer)
    except Exception as e:
        print(e)
        raise
    
    nivel_tanque_1 = buffer[0] * (30 / 5) 
    nivel_tanque_2 = buffer[1] * (30 / 5) 
    corrente_bomba = buffer[2] 
    print(f'Nivel tanque 1: {round(nivel_tanque_1, 2)} cm')
    print(f'Nivel tanque 2: {round(nivel_tanque_2, 2)} cm')
    print('Corrente na bomba: ', )

    if nivel_tanque_1 == 0.0 and nivel_tanque_2 == 0.0 and corrente_bomba == 0.0:
        desligar_bomba(card)
        print('Erro: erro na aquisição dos sinais analógicos - Reinicie o módulo Q8-USB')
        exit()

    return nivel_tanque_1, nivel_tanque_2, corrente_bomba
