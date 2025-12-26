# 🏥 Frontend Guide v3 - The Clinical Cockpit

**Hedef Kitle:** Doktorlar (Hız ve Bilgiye aç kullanıcılar).
**Tasarım Dili:** "Bloomberg Terminali" gibi. Yoğun veri, karanlık mod, yüksek kontrast, gereksiz boşluk yok.

## 1. Doctor Dashboard (Main Hub) 🖥️
Burası doktorun gününü geçirdiği yer.

### A. Sol Panel: Akıllı Hasta Listesi (Smart Queue)
*   **Sıralama:** Standart isim sırası DEĞİL. **Risk Score (Azalan)** veya **Triage Aciliyeti**ne göre sıralı.
*   **Görsel:** Her hastanın yanında küçük bir "Status Dot" (🔴/🟡/🟢).
*   **Hızlı Bilgi:** Listede sadece isim değil, "Ana Şikayet" ve "Son Geliş Tarihi" de yazar.

### B. Orta Panel: Clinical Command Center 📊
Seçili hasta için detaylar.
*   **Header:** Hasta Adı, Yaş, Kan Grubu, Allerjiler (Büyük kırmızı bant ile).
*   **4-Way Risk Grid:** Ekranı 4'e böl. Kalp, Diyabet, Böbrek, İnme grafiklerini kompakt göster.
*   **Timeline:** Hastanın geçmiş ziyaretleri, ilaç değişimleri ve lab sonuçları yatay bir zaman çizelgesinde.

### C. Sağ Panel: AI Copilot (Sidekick) 🤖
*   **Active Analysis:** Doktor gezinirken sürekli arkaplanda çalışır.
*   **Alerts:** "Potansiyel İlaç Etkileşimi!", "Diyabet riski geçen aya göre %10 arttı."
*   **Action Buttons:**
    *   `[Generate Epikriz]` (Raporu yazar)
    *   `[Order Labs]` (Tahlil ister)
    *   `[Prescribe]` (Reçete yazar)

## 2. Emergency Triage Modu 🚨
Tek tuşla (`Ctrl+E` veya Navbar butonu) açılır.
*   **UI:** Siyah arka plan, devasa inputlar.
*   **Inputs:** Nabız, Tansiyon, SPO2, Bilinç.
*   **Output:** Ekranın tamamı KIRMIZI, SARI veya YEŞİL olur. Fontlar devasa.

## 3. Patient Companion (Mobil Web) 📱
Bu sadece doktorun hastasına "link" olarak attığı basit bir ekran.
*   "Sonuçlarım ne anlama geliyor?"
*   "İlacımı ne zaman alayım?"
*   Doktora veri gönderme (Check-in).

---

**Teknik Notlar:**
*   Koyu Tema (Dark Mode) varsayılan olsun. Göz yormaz.
*   Klavye kısayolları ekle (`Cmd+K` ile hasta ara).
*   Data Grid kütüphanesi kullan (AG Grid veya TanStack Table).
