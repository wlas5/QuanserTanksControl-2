from datetime import datetime, date
import os

today = 0
last_line = 0

def criar_datalog(data):
    try:
        global last_line, today
        
        path = "datalog"
# Check whether the specified path exists or not
        isExist = os.path.exists(path)
        try:
            if not isExist:

        # Create a new directory because it does not exist
                os.makedirs(path)
                print("The new directory is created!")
        except:
            print("")
            print("ERRO NA CRIAÇÃO DA PASTA DO DATALOG")
            raise
 



        print(f'{date.today().strftime("%d%m%y")}\n')
        today = date.today().strftime("%d%m%y")
        line = 0 

        ### Executado uma vez no início
        #verifica a numeração do arquivo
        
        with open(f"datalog/{today}.txt",'a+') as f:
            f.seek(0)
            for line in f:
                pass #print(line)
            last_line = int(line)
            print(f"Last line 1: {last_line}")

            last_line += 1
            f.write(f"{last_line}\n")
        
        with open(f'datalog/{today} - {last_line}.csv', 'a+') as ff:
            ff.write(data)
            
    except:
        print("")
        print("ERRO NA CRIAÇÃO DO DATALOG")
        raise

    
def salvar_dados(i):
    global today, last_line
    try:
        with open(f'datalog/{today} - {last_line}.csv', 'a+') as ff:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ff.write(f"{now};{i}\n")
    except:
        print("")
        print("ERRO NA ESCRITA DO DATALOG")
        raise 
##executado no loop



#criar_datalog()

#i = 0 
#while i < 50:
#    salvar_dados(i)
#    i += 1;
