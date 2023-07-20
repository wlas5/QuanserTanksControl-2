#coding=utf8


import time
from datetime import datetime, date
from quanser.hardware import HIL, HILError
import os
import ifb_arte
import smart_datalog
from io_quanser import leia, desligar_bomba, aplica_controle, trava
import matplotlib.pyplot as plt


referencia = 20
#nivel_tanque_2 = 0.0

malha_fechada = True
pid = True
mudar_referencia = True
sinal_malha_aberta = 3
save_data = True

if malha_fechada and pid:
    on_off = False
if malha_fechada and not pid:
    on_off = True

kp = 1
ki = 1.5

# Intervalo de amostragem 
sampleTime = 0.4


card = HIL()
card.open("q8_usb","0")

def main():
    erro_ant = 0    

    try:
        
        cabecalho = "Hora;referencia;nivel_tanque1;nivel_tanque2;sinal_controle;sinal_aplicado\n"
        smart_datalog.criar_datalog(cabecalho)

        # Preparar o gráfico
        plt.ion()  # Modo de plotagem interativo
        fig, ax = plt.subplots()
        x_vals = []
        y_vals_tanque1 = []
        y_vals_tanque2 = []
        y_vals_referencia = []
        y_vals_sinal_controle = []
        line_tanque1, = ax.plot(x_vals, y_vals_tanque1, label='Tanque 1')
        line_tanque2, = ax.plot(x_vals, y_vals_tanque2, label='Tanque 2')
        line_referencia, = ax.plot(x_vals, y_vals_referencia, label='Referencia')
        line_sinal_controle, = ax.plot(x_vals, y_vals_sinal_controle, label='Sinal de Controle')
        ax.legend()

        while True:
            print("")
            print(f'{date.today().strftime("%d/%m/%y")}\n')
            print("")
            print(f'Tempo de execução: {time.perf_counter()}')
            startTime = time.perf_counter()
            start = datetime.now()
            if time.perf_counter() > 30:
                global referencia
                referencia = 10

            #leitura das variáveis
            nivel_tanque_1, nivel_tanque_2, corrente_bomba = leia(card)


            #controle 
            erro = referencia - nivel_tanque_2

            if malha_fechada:
                if pid:
                    u = kp * erro + ki * erro_ant * sampleTime
                    #u = kp * erro
                    erro_ant += erro 
                    erro_ant = max(min(erro_ant,3),-3) #limita a parcela integrativa entre -3 e 3
                if on_off:  
                    if erro > 1:
                        u = 4
                    elif erro < -1:
                        u =-4
                        
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

            # Atualizar o gráfico
            x_vals.append(len(x_vals))
            y_vals_tanque1.append(nivel_tanque_1)
            y_vals_tanque2.append(nivel_tanque_2)
            y_vals_referencia.append(referencia)
            y_vals_sinal_controle.append(aplica_controle(card,u))
            line_tanque1.set_xdata(x_vals)
            line_tanque1.set_ydata(y_vals_tanque1)
            line_tanque2.set_xdata(x_vals)
            line_tanque2.set_ydata(y_vals_tanque2)
            line_referencia.set_xdata(x_vals)
            line_referencia.set_ydata(y_vals_referencia)
            line_sinal_controle.set_xdata(x_vals)
            line_sinal_controle.set_ydata(y_vals_sinal_controle)
            ax.relim()
            ax.autoscale_view()

            plt.draw()
            plt.pause(0.001)

        

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


    
