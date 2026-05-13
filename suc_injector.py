import time
import requests
import os
from ppadb.client import Client as AdbClient

# Configurações do SUC SOFTWARES
FIREBASE_URL = "SUA_URL_DO_FIREBASE_AQUI/.json"
SIG_URL = "https://raw.githubusercontent.com/SEU_USER/suc-softwares/main/signatures.json"

class SucInjector:
    def __init__(self):
        self.client = AdbClient(host="127.0.0.1", port=5037)
        self.device = None

    def get_device(self):
        devices = self.client.devices()
        if devices:
            self.device = devices[0]
            return True
        return False

    def clean_and_bypass(self):
        """Protocolo Anti-Analista: Limpa logs e desativa ADB"""
        if self.device:
            print("\n[SUC] ALERTA: EXECUTANDO BYPASS DE SEGURANÇA...")
            self.device.shell("su -c 'logcat -c && rm -rf /data/local/tmp/*'")
            self.device.shell("su -c 'settings put global adb_enabled 0'")
            print("[SUC] TUDO LIMPO. NENHUM RASTRO ENCONTRADO.")

    def auto_scan_inject(self, feature, sig, patch):
        pid = self.device.shell("pidof com.dts.freefireth").strip()
        if not pid: return
        
        # Procura a assinatura na memória RAM (Auto Scan)
        find_addr = f"su -c 'grep -obU -P \"\\x{sig.replace(' ', '\\x')}\" /proc/{pid}/maps | head -n 1'"
        addr = self.device.shell(find_addr)
        
        if addr:
            offset = addr.split(':')[0]
            # Injeta o patch sem criar arquivos (Memory-only)
            self.device.shell(f"su -c 'echo -ne \"\\x{patch.replace(' ', '\\x')}\" | dd of=/proc/{pid}/mem bs=1 seek={offset} conv=notrunc'")
            print(f"[SUC] {feature} Ativado!")

def main():
    suc = SucInjector()
    print(">>> SUC SOFTWARES: AGUARDANDO CONEXÃO USB...")

    while True:
        try:
            if not suc.device:
                if suc.get_device(): print(">>> HARDWARE CONECTADO.")
            
            if suc.device:
                # Puxa comandos do Firebase e assinaturas do GitHub
                data = requests.get(FIREBASE_URL).json()
                sigs = requests.get(SIG_URL).json()

                if data.get("aim") == 1:
                    suc.auto_scan_inject("AIMBOT", sigs['COMBAT']['AIM_ASSIST']['sig'], sigs['COMBAT']['AIM_ASSIST']['patch'])
                
                if data.get("panic") == 1:
                    suc.clean_and_bypass()
                    break

            time.sleep(1)
        except Exception:
            suc.clean_and_bypass()
            break

if __name__ == "__main__":
    main()
