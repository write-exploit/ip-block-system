from flask import request,Flask
import json 
from datetime import datetime
import re
import ipaddress

app = Flask( __name__)

def veri_ekle(dosya:str,ekle:dict):

    json_dosyası = open(dosya, 'r', encoding='utf8')
    try:
        veriler = json.load(json_dosyası)
    except json.decoder.JSONDecodeError:
        veriler = {}

    veriler.update(ekle)

    with open(dosya,'w') as yeni_içerik:
        json.dump(veriler, yeni_içerik, indent=4)

def oku(dosya):
    with open(dosya,'r',encoding='utf8') as okunacak_json:
        try: # dosya içeriği boşsa hata verir
            return json.load(okunacak_json)
        except json.decoder.JSONDecodeError:
            pass

def veri_sil(dosya: str, silinecek_deger:str):

    with open(dosya, 'r', encoding='utf8') as json_dosyası:
        veriler = json.load(json_dosyası)
            
        with open(dosya,'w',encoding='utf8') as yeni_içerik:
            
            del veriler[silinecek_deger]
        
            json.dump(veriler,yeni_içerik,indent=4)


def zamanı_düzenle(zaman:str):
    düzeltilmiş_zaman = re.split(r'[- :.]',zaman)
    düzenli = list(map(int,düzeltilmiş_zaman))        
    return düzenli


def kontrol(ip_adresi:str):
    
    dosya = 'sifre-denemeleri.json'
    try:
        ipaddress.ip_address(ip_adresi) # normal ip adresi yazmazsanız kod çalışmaz deneme yapmak istiyorsanız burayı kaldırabilirsiniz
    except:
        return

    içerik = oku(dosya)

    if içerik: # içerik boş değilse
        if any(i for i in içerik.keys() if i == ip_adresi):
            ip_adresi_ekle = False
        else:
            ip_adresi_ekle = True
    else:
        ip_adresi_ekle = True

    if ip_adresi_ekle == True:
        black_list = oku('blacklist.json')
        sil = False
        if not black_list:
            pass
        else:
            if any(i for i in black_list.keys() if i == ip_adresi): # ip adresi black_list'de mevcutsa
                sil = True
            else:
                sil = False
        if sil:
            zaman = zamanı_düzenle(black_list[ip_adresi])
            eski_zaman = datetime(*zaman)
            simdiki_zaman = datetime.now()
            fark = simdiki_zaman - eski_zaman
            fark_saniye = fark.total_seconds()
            if fark_saniye >= 300: # 5 dakika geçti ise
                veri_sil('blacklist.json',ip_adresi)
                kontrol(ip_adresi)
            else:
                pass

        else:            
            dosya = 'sifre-denemeleri.json'
            yeni_veri = {ip_adresi: 1} # ip adresini 1 deneme yaptı olarak kayıt ediyoruz
            veri_ekle(dosya,yeni_veri)

    else:
        if içerik[ip_adresi] >= 4: # 4'e eşit yada büyükse
            veri_sil(dosya,ip_adresi)
            şuanki_zaman = str(datetime.now()) # şuanki zamanı alıyoruz
            sözlük = {ip_adresi: şuanki_zaman} # ve ip adresini şuanki zaman ile kayıt ediyoruz
            veri_ekle('blacklist.json',sözlük)
        else:
            içerik[ip_adresi] += 1
            veri_ekle(dosya,içerik)

@app.route("/login/",methods=["GET","POST"]) # örnek bir site
def login():
    if request.method == 'POST':
        ip_adresi = request.remote_addr # siteye giren kullanıcının ip adresi
        kontrol(ip_adresi)
        blacklist = oku('blacklist.json')
        if not blacklist:
            pass
        else:
            if any(i for i in blacklist if i == ip_adresi):            
                return '''
                <h1> çok fazla istek yolladığınız için engellendiniz 5 dakika sonra tekrar deneyin</h1>
                '''
            else:
                username = request.form['username']
                password = request.form['password']
                
                if username == 'admin' and password == '123':
                    return '''
                    <h1> giriş başarılı </h1>
                    '''

    return '''
<form action="/login" method="post">
    <h2>login</h2>
        <input type="text" name="username" placeholder="Kullanıcı Adı" required><br><br>
        <input type="text" name="password" placeholder="Şifre" required><br><br>
    <button type="submit">Giriş Yap</button>
</form>
'''
if __name__ == "__main__":
    app.run(debug=True)
