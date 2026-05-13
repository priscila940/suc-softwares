import time
import requests
import os
from ppadb.client import Client as AdbClient

# Configurações do SUC SOFTWARES - Pedro
FIREBASE_URL = "https://suc-4ea3c-default-rtdb.firebaseio.com/.json"
SIG_URL = "https://raw.githubusercontent.com/priscila940/suc-softwares/main/signatures.json"

class SucInjector:
    def __init__(self):
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.device = None

    def get_device(self):
        try:
            devices = self.client.devices()
            if devices:
                self.device = devices[0]
                return True
        except:
            pass
        return False

    def clean_and_bypass(self):
        """Protocolo Anti-Analista: Limpa logs e desativa ADB"""
        if self.device:
            print("\n[SUC] ALERTA: EXECUTANDO BYPASS DE SEGURANÇA...")
            # Limpa logs e arquivos temporários da memória
            self.device.shell("su -c 'logcat -c && rm -rf /data/local/tmp/*'")
            # Desativa o ADB para evitar detecção após o uso
            self.device.shell("su -c 'settings put global adb_enabled 0'")
            print("[SUC] PROTOCOLO FINALIZADO. DISPOSITIVO LIMPO.")

    def auto_scan_inject(self, feature, sig, patch):
        # Verifica se o processo do Free Fire está rodando
        pid = self.device.shell("pidof com.dts.freefireth").strip()
        if not pid: return
        
        # Procura a assinatura na memória RAM (Auto Scan)
        find_addr = f"su -c 'grep -obU -P \"\\x{sig.replace(' ', '\\x')}\" /proc/{pid}/maps | head -n 1'"
        addr = self.device.shell(find_addr)
        
        if addr:
            try:
                offset = addr.split(':')[0]
                # Injeção Volátil: Escreve direto na memória do processo
                self.device.shell(f"su -c 'echo -ne \"\\x{patch.replace(' ', '\\x')}\" | dd of=/proc/{pid}/mem bs=1 seek={offset} conv=notrunc'")
                print(f"[SUC] {feature} Aplicado com sucesso!")
            except:
                print(f"[SUC] Falha na injeção de {feature}")

def main():
    suc = SucInjector()
    print(">>> SUC SOFTWARES | DESENVOLVIDO POR PEDRO")
    print(">>> STATUS: AGUARDANDO CONEXÃO USB...")

    while True:
        try:
            if not suc.device:
                if suc.get_device(): 
                    print(">>> DISPOSITIVO RECONHECIDO. SINCRONIZANDO COM PAINEL...")
            
            if suc.device:
                # Consulta o Firebase para ver quais funções você ativou no site
                response = requests.get(FIREBASE_URL)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Busca as assinaturas hexadecimais no seu GitHub priscila940
                    try:
                        sigs = requests.get(SIG_URL).json()
                    except:
                        sigs = None

                    if data and sigs:
                        # Executa as funções baseadas no seu index.html
                        if data.get("aim") == 1:
                            suc.auto_scan_inject("AIMBOT", sigs['COMBAT']['AIM_ASSIST']['sig'], sigs['COMBAT']['AIM_ASSIST']['patch'])
                        
                        if data.get("recoil") == 1:
                            suc.auto_scan_inject("NO_RECOIL", sigs['COMBAT']['NO_RECOIL']['sig'], sigs['COMBAT']['NO_RECOIL']['patch'])

                        # Se clicar no botão vermelho de Pânico no site
                        if data.get("panic") == 1:
                            suc.clean_and_bypass()
                            # Reseta o status de pânico no Firebase para a próxima vez
                            requests.put(FIREBASE_URL.replace(".json", "panic.json"), json=0)
                            break

            time.sleep(1.5) 
        except Exception as e:
            print(f">>> ERRO DE CONEXÃO: {e}")
            suc.clean_and_bypass()
            break

if __name__ == "__main__":
    main()
