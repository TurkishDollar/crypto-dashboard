Juno₿TWHunteR uygulamasını tamamen düzelt ve profesyonel hale getir.

ÖNEMLİ:
Ben Python kodu bilmiyorum. Bana parça parça kod verme. Mevcut app.py dosyasının tamamını kendin düzenle ve çalışır TAM DOSYA olarak oluştur. Mevcut kodu tamamen değiştirmen gerekiyorsa değiştir. Ben sadece kopyala-yapıştır yapacağım.

AMAÇ:
Juno₿TWHunteR gerçek zamanlı kripto piyasa istihbarat uygulamasıdır.

KESİNLİKLE:
- MOCK DATA KULLANMA.
- DEMO DATA KULLANMA.
- RASTGELE ÜRETİLMİŞ FİYAT KULLANMA.
- SAHTE SİNYAL ÜRETME.
- Binance API kullanma; bulunduğum ortamda Binance API 451 restricted-location hatası veriyor.
- Ana veri kaynağı OKX olsun.
- Gerçek OKX public API ve OKX public WebSocket kullan.
- API verisi alınamazsa sahte veri göstermek yerine açıkça OFFLINE/HATA göster.
- Uygulama hiçbir durumda sahte veriyle çalışmaya devam etmesin.

BAĞIMLILIKLAR:
Gerekli paketleri otomatik olarak requirements.txt içine ekle:
streamlit
pandas
requests
websocket-client

Eğer plotly kullanmıyorsan kesinlikle import etme.
Eksik paket yüzünden ModuleNotFoundError oluşmasına izin verme.

OKX VERİLERİ:
Ana market:
BTC-USDT-SWAP

Kullanıcı sidebar üzerinden coin değiştirebilsin.
Örnek:
BTC
ETH
SOL
XRP
DOGE

Girilen coin otomatik olarak:
COIN-USDT-SWAP
formatına dönüştürülsün.

GERÇEK REST VERİLERİ:
OKX public REST API üzerinden:
- Son fiyat
- 24H değişim
- 24H high
- 24H low
- 24H volume
- quote volume
- mum verileri

alınsın.

GERÇEK WEBSOCKET:
OKX public WebSocket kullan.

Aşağıdaki kanalları mümkün olduğunca gerçek zamanlı kullan:
- tickers
- trades
- books5

WebSocket bağlantısı:
wss://ws.okx.com:8443/ws/v5/public

WebSocket otomatik reconnect yapmalı.
Bağlantı koparsa yeniden bağlanmalı.
Bağlantı durumunu ekranda göster:

🟢 OKX WEBSOCKET — LIVE
🟡 OKX WEBSOCKET — RECONNECTING
🔴 OKX WEBSOCKET — OFFLINE

REST API durumunu da göster:

🟢 OKX REST API — ONLINE
🔴 OKX REST API — OFFLINE

GERÇEK CANLI FİYAT:
WebSocket ticker verisinden gerçek zamanlı fiyat göster.

Ekranda:
💰 BTC/USDT PERPETUAL
LIVE PRICE

göster.

BID / ASK:
Gerçek WebSocket order book verisinden:
- Bid
- Ask
- Bid Size
- Ask Size
- Spread
- Order Book Imbalance

göster.

ORDER BOOK IMBALANCE:
Gerçek bid ve ask miktarlarını kullan.

Formül:

imbalance =
(bid_size - ask_size) /
(bid_size + ask_size) * 100

Sonucu:
+% değer = alıcı baskısı
-% değer = satıcı baskısı

olarak göster.

GERÇEK ALIM/SATIM AKIŞI:
OKX WebSocket trades kanalından gerçek işlemleri al.

Her işlem için:
- BUY veya SELL
- fiyat
- miktar
- işlem değeri
- UTC saat

göster.

BUY işlemlerini ekranda belirgin YEŞİL göster.
SELL işlemlerini belirgin KIRMIZI göster.

FLOW:
Gerçek WebSocket işlemlerinden:
BUY FLOW
SELL FLOW

hesapla.

Flow imbalance:

(buy_volume - sell_volume) /
(buy_volume + sell_volume) * 100

olarak hesaplanmalı.

WHALE SCANNER:
Gerçek trades verisini kullan.

Sidebar'da:
🐋 Whale Threshold (USDT)

ayarını oluştur.

Varsayılan:
100000 USDT

Kullanıcı değiştirebilsin.

İşlem değeri threshold'dan büyük/eşitse whale olarak göster.

BUY whale:
🟢 BUY WHALE

SELL whale:
🔴 SELL WHALE

göster.

Kesinlikle sahte whale üretme.

TEKNİK ANALİZ:
Gerçek OKX mumlarından hesapla:

EMA 9
EMA 21
EMA 50
EMA 200
RSI 14
VWAP
Volume
Volume MA20
Volume Ratio

Bunların tamamı gerçek mum verisinden hesaplanmalı.

SİNYAL MOTORU:
Juno₿TWHunteR şu üç sonuçtan yalnızca birini üretsin:

🟢 LONG
🔴 SHORT
⚪ WAIT

Sinyal motoru aşağıdaki gerçek verileri birlikte değerlendirsin:

1. EMA 9 / EMA 21
2. EMA 50
3. EMA 200
4. RSI
5. VWAP
6. Volume Ratio
7. Order Book Imbalance
8. BUY/SELL Flow Imbalance
9. Whale BUY/SELL aktivitesi

ÖNEMLİ:
Sadece tek bir indikatöre bakarak LONG veya SHORT verme.

Çelişkili piyasa koşullarında WAIT üret.

Örneğin:
EMA bullish ama order flow güçlü bearish ise körü körüne LONG verme.

SİNYAL GÜCÜ:
Eski sistemdeki yapay "%92 güven" mantığını kullanma.

Bunun yerine:
Sinyal Gücü: 0–100

puanı oluştur.

Bu değer kesinlikle "işlemin kazanma ihtimali %92" gibi gösterilmesin.

Başlığını:
🎯 SİNYAL GÜCÜ

olarak göster.

LONG:
Yeşil arka plan
Yeşil yazı
Belirgin büyük LONG kutusu

SHORT:
Kırmızı arka plan
Kırmızı yazı
Belirgin büyük SHORT kutusu

WAIT:
Gri/sarı ton
Belirgin WAIT kutusu

Kullanıcı ekrana baktığında LONG ve SHORT ilk bakışta net şekilde ayırt edilebilmeli.

SİNYAL NEDENLERİ:
Sinyalin neden üretildiğini Türkçe olarak göster.

Örnek:

EMA 9 > EMA 21 → kısa vadeli bullish
Fiyat EMA 200 üzerinde → ana trend bullish
RSI 56 → bullish momentum
Order Book → alıcı baskısı
Flow → BUY baskısı
Whale Activity → BUY

Ancak yalnızca gerçek verilerden gelen nedenleri göster.

GRAFİK:
Mevcut basit line chart yerine mümkün olduğunca profesyonel bir gerçek mum grafiği oluştur.

Plotly kullanacaksan requirements.txt içine:
plotly

ekle.

Eğer Plotly kullanmıyorsan import plotly yapma.

Grafikte:
- Candlestick
- EMA 9
- EMA 21
- EMA 50
- EMA 200
- mümkünse VWAP

göster.

Grafik:
- zoom
- pan
- mouse hover
- timeframe değişimi

desteklesin.

TIMEFRAME:
Sidebar'da:

1m
3m
5m
15m
30m
1H
4H
1D

seçenekleri olsun.

OKX'in desteklediği uygun bar değerlerini kullan.

EKRAN TASARIMI:
Tamamen koyu profesyonel terminal görünümü oluştur.

Başlık:

Juno₿TWHunteR 🌎₿

Alt başlık:

REAL-TIME OKX MARKET INTELLIGENCE

Üst bölümde:
- LIVE PRICE
- 24H CHANGE
- 24H HIGH
- 24H LOW

göster.

Sonra:

🌐 DATA CONNECTION
💰 MARKET
📚 ORDER BOOK
⚡ REAL BUY/SELL FLOW
🐋 WHALE SCANNER
🎯 JUNO₿TWHUNTER SIGNAL
📈 TECHNICAL ANALYSIS
🧠 SIGNAL REASONS
📊 REAL-TIME CHART
⚡ LIVE TRADES

bölümleri olsun.

VERİ DURUMU:
Ekranın altında:

🟢 OKX REAL DATA
🟢 WEBSOCKET LIVE
❌ MOCK DATA
❌ DEMO DATA

göster.

Son güncelleme UTC saatini göster.

HATA YÖNETİMİ:
Kodda hiçbir yerde boş veya bozuk try/except yapısı bırakma.

SyntaxError oluşturma.

Özellikle:
try:
    ...
except:
    ...

bloklarının eksik kalmadığından emin ol.

Her fonksiyon düzgün kapanmalı.

Tüm parantezleri, girintileri ve Python syntax'ını kontrol et.

Uygulama başlatıldığında siyah boş ekran oluşmasın.

API başarısızsa kullanıcıya anlaşılır hata mesajı göster.

API'den veri gelmiyorsa:
"Gerçek piyasa verisi alınamadı. Sahte veri gösterilmiyor."
mesajını göster.

AUTO REFRESH:
WebSocket canlı akışı kullanıldığı için gereksiz yere her 1-2 saniyede tüm REST API'yi tekrar çağırma.

REST verilerini makul aralıklarla yenile.

WebSocket gerçek zamanlı veriyi mümkün olduğunca sürekli kullansın.

Streamlit üzerinde stabil çalışması için gerekiyorsa kontrollü ekran yenileme kullan.

ÖNEMLİ:
Streamlit Cloud ortamında çalışacak şekilde tasarla.

Thread/WebSocket kullanımını Streamlit ile uyumlu ve güvenli yap.

WebSocket thread'i uygulamayı kilitlemesin.

Bağlantı koparsa uygulama çökmemeli.

WebSocket yeniden bağlanabilmeli.

SON KONTROL:
Kod tamamlandıktan sonra kendi içinde kontrol et:

1. SyntaxError var mı?
2. Eksik import var mı?
3. requirements.txt eksik mi?
4. plotly import ediliyor ama requirements.txt'de yok mu?
5. Binance API yanlışlıkla kullanılıyor mu?
6. Mock/demo veri var mı?
7. Sahte fiyat üreten kod var mı?
8. Sahte whale var mı?
9. Sahte sinyal var mı?
10. OKX REST çalışıyor mu?
11. OKX WebSocket doğru endpoint'i kullanıyor mu?
12. LONG yeşil mi?
13. SHORT kırmızı mı?
14. WAIT belirgin mi?
15. Gerçek BUY/SELL trades gösteriliyor mu?
16. Gerçek order book gösteriliyor mu?
17. Whale scanner gerçek trades kullanıyor mu?
18. Teknik indikatörler gerçek mumlardan mı hesaplanıyor?
19. Uygulama veri alınamadığında sahte veri göstermiyor mu?
20. Streamlit Cloud üzerinde çalışabilecek durumda mı?

Bütün bunları düzelttikten sonra bana sadece tamamlanmış, çalışır proje dosyalarını oluştur.

BEN KOD BİLMİYORUM.
BU NEDENLE PARÇA PARÇA TALİMAT VERME.
MEVCUT KODU TAMAMEN DÜZELT.
app.py VE GEREKLİ requirements.txt DOSYASINI HAZIRLA.

AMAÇ:
Önce çalışan ve stabil gerçek OKX REST + WebSocket sistemi oluştur.
Daha sonra bu temel üzerine daha gelişmiş AI/sinyal motoru ekleyeceğiz.

KESİNLİKLE GERÇEK VERİ.
KESİNLİKLE MOCK YOK.
KESİNLİKLE DEMO YOK.
