#coding=utf8


import time
from datetime import datetime, date
from quanser.hardware import HIL, HILError
import os
import ifb_arte
import smart_datalog
from io_quanser import leia, desligar_bomba, aplica_controle, trava

referencia = 20
#nivel_tanque_2 = 0.0

malha_fechada = True
sinal_malha_aberta = 3
save_data = True

kp = 1
ki = 1.5

# Intervalo de amostragem 
sampleTime = 0.3


card = HIL()
card.open("q8_usb","0")

def main():
    erro_ant = 0    

    try:
        
        cabecalho = "Hora;referencia;nivel_tanque1;nivel_tanque2;sinal_controle;sinal_aplicado\n"
        smart_datalog.criar_datalog(cabecalho)

        while True:
            print("")
            print(f'{date.today().strftime("%d/%m/%y")}\n')
            startTime = time.perf_counter()
            
            start = datetime.now()

            #leitura das variáveis
            nivel_tanque_1, nivel_tanque_2, corrente_bomba = leia(card)

            #controle 
            erro = referencia - nivel_tanque_2

            if malha_fechada:
                u = kp * erro + ki * erro_ant * sampleTime
                #u = kp * erro
                erro_ant += erro 
                erro_ant = max(min(erro_ant,3),-3) #limita a parcela integrativa entre -3 e 3
            else:
                u = sinal_malha_aberta

            aplica_controle(card,u)
            trava(card,nivel_tanque_1,nivel_tanque_2, u)


            print("Erro: ", round(erro, 2))
            print("Erro ant: ", round(erro_ant, 2))
            print('Sinal de controle calculado: ', round(u,2))
            print(f'Sinal de controle aplicado: {aplica_controle(card,u):.2f}')

            #dados para o datalog
            if save_data:
                data = f"{referencia};{nivel_tanque_1:.2f};{nivel_tanque_2:.2f};{u:.2f};{aplica_controle(card,u):.2f}"
                smart_datalog.salvar_dados(data)

            #rotina de controle de tempo: 
            endTime = time.perf_counter()
            deltaTime = endTime-startTime
            sleepTime = sampleTime - deltaTime
            time.sleep(sleepTime)
            
            
            os.system('cls') #para limpar a tela
            ifb_arte.ifb_arte() #arte principal da tela

            print("Invervalo do código: ", round(deltaTime, 3))
            print("Sleep time: ", round(sleepTime,3))
            print("Invervalo de amostragem: ", round(time.perf_counter()-startTime, 3))

            
                
    except HILError as e:
        print(e.get_error_message())
    except KeyboardInterrupt:
        desligar_bomba(card)
        print("Aborted by user.")
    except Exception as e:
        desligar_bomba(card)
        print(" ")
        print(e)
        print(" ")
        print("Algum erro no programa fez encerrar!")
    finally:
        if card.is_valid():
            card.close()



if __name__ == "__main__":
    main()


    
