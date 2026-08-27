Juno₿TWHunteR için Streamlit tabanlı gerçek zamanlı kripto piyasa istihbarat uygulamasını baştan ve TEK PARÇA olarak oluştur.

ÇOK ÖNEMLİ:
- SADECE GERÇEK PİYASA VERİSİ KULLAN.
- MOCK DATA KULLANMA.
- DEMO DATA KULLANMA.
- RANDOM DATA KULLANMA.
- SAHTE / TÜRETİLMİŞ FİYAT KULLANMA.
- API başarısız olduğunda kesinlikle sahte veri gösterme.
- Veri alınamazsa ekranda açıkça "GERÇEK VERİ ALINAMIYOR" ve gerçek hata mesajını göster.
- Uygulama hiçbir veriyi gerçekmiş gibi uydurmasın.
- Özellikle Futures fiyatını Spot fiyatından matematiksel olarak üretme.

VERİ KAYNAĞI:
İlk aşamada Binance resmi public market API'larını kullan.

Spot:
https://api.binance.com

USDT-M Futures:
https://fapi.binance.com

API anahtarı gerektirmeyen public market endpointlerini kullan.

GERÇEK VERİLER:
- Binance Spot gerçek fiyat
- Binance USDT-M Perpetual gerçek fiyat
- 24 saatlik gerçek değişim
- Gerçek 24h high/low
- Gerçek hacim
- Gerçek OHLCV mum verileri
- Gerçek işlem sayısı
- Gerçek taker buy/sell verileri
- Gerçek Futures market verileri
- Gerçek aggTrades verileri

VERİ DOĞRULAMA:
Her API isteğinde HTTP status code kontrol et.
Timeout ve connection hatalarını yakala.
JSON/API hata mesajlarını kullanıcıya göster.
API başarısız olduğunda veri alanında "N/A" veya "VERİ ALINAMIYOR" göster.
Eski/stale veriyi yeni veriymiş gibi gösterme.
Spot API ve Futures API bağlantısını uygulama açılışında ayrı ayrı test et.
Ekranda:
🟢 SPOT API: ONLINE
🟢 FUTURES API: ONLINE
veya
🔴 SPOT API: OFFLINE
🔴 FUTURES API: OFFLINE
şeklinde bağlantı durumu göster.

ARAYÜZ:
Koyu profesyonel bir trading dashboard tasarla.

Başlık:
Juno₿TWHunteR 🌎₿

Alt başlık:
REAL-TIME CRYPTO MARKET INTELLIGENCE

Alt bilgi:
REAL DATA ONLY — NO MOCK / NO DEMO DATA

Ana ekranda büyük şekilde:

🟢 LONG
🔴 SHORT
⚪ WAIT

LONG kesinlikle yeşil renkte ve çok belirgin olsun.
SHORT kesinlikle kırmızı renkte ve çok belirgin olsun.
WAIT gri/nötr renkte olsun.

Sinyalin hemen altında:
GÜVEN: XX%

Sinyal kartı mobil telefonda da çok net okunabilsin.

COIN SEÇİMİ:
Varsayılan:
BTCUSDT

Kullanıcı farklı Binance USDT-M perpetual coin seçebilsin.

Timeframe seçenekleri:
1m
3m
5m
15m
30m
1h
4h
1d

TEKNİK ANALİZ:
Gerçek Binance Futures OHLCV verilerinden hesapla:

- EMA 9
- EMA 21
- EMA 50
- EMA 200
- RSI 14
- VWAP
- Volume
- Volume MA20
- Volume Ratio
- Fiyatın EMA'lara uzaklığı
- Trend yönü
- Momentum

RSI, EMA ve VWAP değerlerini gerçek mum verilerinden hesapla.

SİNYAL MOTORU:
Sinyal rastgele oluşturulmayacak.

EMA 9/21
EMA 50
EMA 200
RSI
VWAP
Volume Ratio
fiyat hareketi
ve mümkün olan gerçek order-flow verilerini birlikte değerlendir.

Tek bir ana karar üret:

LONG
SHORT
WAIT

Sinyal nedenlerini ekranda açıkça göster.

Örnek:
EMA 9 > EMA 21 → bullish
Fiyat EMA 200 üzerinde → ana trend bullish
RSI → momentum
Fiyat VWAP üzerinde
Hacim → ortalamanın X katı

Sinyal motoru yeterince güçlü bir yön göstermiyorsa:
WAIT

Sinyal kesinlikle garanti olarak sunulmasın.
Bu sistem teknik piyasa analizi üretir; kesin kazanç iddiasında bulunmaz.

GÜVEN PUANI:
0-100 arasında hesapla.

Ancak güven yüzdesi tamamen rastgele veya sabit olmasın.
Kullanılan gerçek teknik göstergelerin uyumuna göre hesapla.

GRAFİK:
Gerçek Binance Futures mum verilerini göster.
Sadece basit line chart kullanmak yerine mümkünse TradingView benzeri candlestick görünümü oluştur.

Grafikte:
- Mumlar
- EMA 9
- EMA 21
- EMA 50
- EMA 200
- VWAP
gösterilebilsin.

Grafik:
- zoom
- pan
- timeframe değiştirme
- responsive/mobile görünüm
özelliklerine sahip olsun.

WHALE SCANNER:
Binance Futures gerçek aggTrades verisini kullan.

Son büyük işlemleri göster.

Her işlem için:
- BUY / SELL
- fiyat
- miktar
- USDT işlem değeri
- zaman

Varsayılan whale threshold:
100000 USDT

Kullanıcı threshold değiştirebilsin.

Whale işlemlerinde:
BUY = yeşil
SELL = kırmızı

ÖNEMLİ:
Whale Scanner'da "100.000 USDT üzeri işlem" ile "gerçek balina/tekil yatırımcı" kavramlarını birbirine karıştırma.
Veri sadece Binance'ın gerçek aggregate trade verisidir.
Bunu kullanıcıya açıkça belirt.

GERÇEK ORDER FLOW:
Mümkün olduğu kadar Binance Futures public market verilerinden:
- aggressive buy volume
- aggressive sell volume
- buy/sell imbalance
- taker buy/sell
verilerini hesapla.

Ekranda:
BUY PRESSURE
SELL PRESSURE
ORDER FLOW IMBALANCE
göster.

PRICE PANEL:
Üst bölümde:

BINANCE SPOT
$ gerçek spot fiyat

BINANCE USDT-M PERPETUAL
$ gerçek futures fiyat

24H CHANGE
gerçek %

24H HIGH
gerçek $

24H LOW
gerçek $

24H VOLUME
gerçek değer

Spot ve Futures fiyatlarını birbirinden bağımsız olarak API'dan al.
KESİNLİKLE:
Spot × 1.0002
veya herhangi başka bir formülle Futures fiyatı üretme.

CANLI VERİ:
İlk sürümde 5 saniyelik polling kullanılabilir ancak bunu güvenli şekilde yap.

Uygulama:
- veri güncellendiğinde son güncelleme zamanını göster
- veri alınamazsa hata durumunu göster
- sonsuz/kararsız rerun döngüsü oluşturma
- API rate limitlerine dikkat et

Daha profesyonel ikinci aşama için kodu WebSocket'e geçmeye uygun şekilde modüler tasarla.

İKİNCİ AŞAMAYA HAZIRLIK:
Kod yapısını gelecekte aşağıdakileri ekleyebileceğimiz şekilde oluştur:

1. Binance WebSocket
2. Gerçek zamanlı fiyat akışı
3. Gerçek zamanlı trades
4. Gerçek zamanlı aggTrades
5. Gerçek order-flow
6. Gerçek order-book depth
7. Bid/Ask imbalance
8. Whale alert
9. Çoklu timeframe analizi
10. Multi-exchange veri karşılaştırması
11. Daha gelişmiş LONG/SHORT/WAIT sinyal motoru

İLK AŞAMADA API KEY GEREKTİRMEYEN PUBLIC MARKET DATA KULLAN.
Kullanıcı hesabı, emir verme veya otomatik trade özelliği oluşturma.
SADECE MARKET DATA VE ANALİZ.

HATA YÖNETİMİ:
Kodun hiçbir yerinde:

except Exception:
    return None

şeklinde hatayı tamamen gizleme.

Hata olduğunda:
- hangi endpoint
- hangi API
- HTTP status
- Binance hata mesajı
- connection/timeout bilgisi

kullanıcıya okunabilir şekilde göster.

Örneğin:

🔴 BINANCE FUTURES API OFFLINE
Endpoint: /fapi/v1/...
Hata: ...
HTTP: ...

Böylece uygulama hata verdiğinde problemi teşhis edebileyim.

DEPENDENCIES:
Gerekli Python paketlerini açıkça belirt ve mümkünse requirements.txt oluştur:

streamlit
pandas
requests
plotly

Candlestick grafik için Plotly kullan.

MOBİL TASARIM:
Uygulama telefon ekranında düzgün görünsün.
Ana LONG/SHORT/WAIT sinyali ekranda en belirgin unsur olsun.
Kartlar responsive olsun.
Sidebar mobilde kullanılabilir olsun.

ALT BÖLÜM:
Gerçek veri durumunu göster:

🟢 LIVE REAL DATA
Binance Spot: ONLINE
Binance Futures: ONLINE

Last update:
UTC zamanı

Türkiye saati:
UTC+3

Mock Data: DISABLED
Demo Data: DISABLED

KODU TAMAMEN ÇALIŞIR HALDE TEK PARÇA OLUŞTUR.
Yarım kod bırakma.
Eksik fonksiyon bırakma.
Placeholder veri bırakma.
Mock/demo veri ekleme.

Uygulama başlatıldığında önce Binance bağlantılarını test etsin.
Bağlantı başarısızsa nedenini açıkça göstersin ve sahte veri göstermesin.

ÖNEMLİ:
İlk sürümün amacı mükemmel görünmek değil, ÖNCE GERÇEK VERİNİN SORUNSUZ GELMESİDİR.

Önce gerçek Binance verisini çalıştır.
Sonra teknik analiz.
Sonra LONG/SHORT/WAIT.
Sonra Whale Scanner.
Sonra grafik.

Tüm sistemi tek bir Streamlit uygulaması olarak oluştur.
