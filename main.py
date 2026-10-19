#!/usr/bin/env python3
"""
Simulasi Lamport Timestamps
Tugas Mata Kuliah: Sistem Terdistribusi

Program ini menyimulasikan algoritma Lamport Timestamps pada 3 proses
(P1, P2, P3) yang saling mengirim pesan, menghitung timestamp logis
setiap event, lalu memverifikasi konsistensi urutan kejadian.
"""

from collections import defaultdict, deque

# =====================================================================
# BAGIAN 1: Kelas simulator yang menyimpan status logical clock,
#           antrean pesan antar proses, dan log seluruh event.
# =====================================================================


class LamportSimulator:
    """Menyimpan dan memproses simulasi Lamport Timestamps."""

    def __init__(self, daftar_proses):
        # Logical clock tiap proses, diinisialisasi dengan nilai 0.
        self.clock = {p: 0 for p in daftar_proses}

        # Antrean pesan per tujuan. Setiap pesan disimpan sebagai tuple:
        # (id_pesan, pengirim, timestamp_send). Timestamp pesan selalu
        # berasal dari send event yang sesuai, tidak dibuat sembarang.
        self.antrean_pesan = defaultdict(deque)

        # Log seluruh event untuk ditampilkan dalam tabel.
        self.log = []  # berisi dict: no, proses, event, jenis, pesan, ts, keterangan

        # Pemetaan id pesan -> (pengirim, timestamp pada saat send).
        # Dipakai untuk verifikasi konsistensi.
        self.info_send = {}

    # -----------------------------------------------------------------
    # Fungsi pemrosesan event (tiga jenis sesuai ketentuan tugas).
    # -----------------------------------------------------------------

    def proses_internal(self, proses, nama_event, keterangan=""):
        """Internal event: logical clock proses bertambah 1."""
        self.clock[proses] += 1
        self._catat(proses, nama_event, "Internal", "-", self.clock[proses],
                    keterangan or "Proses melakukan kegiatan lokal")

    def kirim(self, proses, nama_event, id_pesan, tujuan, keterangan=""):
        """Send event: clock bertambah 1, timestamp disertakan dalam pesan."""
        self.clock[proses] += 1
        ts = self.clock[proses]
        # Simpan pesan ke antrean tujuan BESERTA timestamp send event asli.
        self.antrean_pesan[tujuan].append((id_pesan, proses, ts))
        self.info_send[id_pesan] = (proses, ts)
        self._catat(proses, nama_event, "Send", f"{id_pesan} -> {tujuan}", ts,
                    keterangan or f"Mengirim pesan {id_pesan} ke {tujuan}")

    def terima(self, proses, nama_event, id_pesan, keterangan=""):
        """Receive event: C = max(C lokal, timestamp pesan) + 1."""
        if not self.antrean_pesan[proses]:
            raise ValueError(
                f"Proses {proses} mencoba menerima {id_pesan}, tetapi antrean kosong!")
        id_asy, pengirim, ts_pesan = self.antrean_pesan[proses].popleft()
        if id_asy != id_pesan:
            raise ValueError(
                f"Pesan berikutnya di antrean {proses} adalah {id_asy}, bukan {id_pesan}!")
        # Rumus aturan ketiga Lamport Timestamps:
        ts_lokal = self.clock[proses]
        self.clock[proses] = max(ts_lokal, ts_pesan) + 1
        self._catat(proses, nama_event, "Receive", f"{id_pesan} dari {pengirim}",
                    self.clock[proses],
                    keterangan or
                    f"Menerima {id_pesan} dari {pengirim}: "
                    f"max(lokal={ts_lokal}, ts_pesan={ts_pesan}) + 1")

    def _catat(self, proses, nama_event, jenis, pesan, ts, keterangan):
        """Mencatat satu event ke log simulasi."""
        self.log.append({
            "no": len(self.log) + 1,
            "proses": proses,
            "event": nama_event,
            "jenis": jenis,
            "pesan": pesan,
            "ts": ts,
            "keterangan": keterangan,
        })


# =====================================================================
# BAGIAN 2: Skenario simulasi (persis 10 event sesuai ketentuan tugas).
# =====================================================================


def jalankan_skenario():
    """Menjalankan skenario 10 event dan mengembalikan objek simulator."""
    sim = LamportSimulator(["P1", "P2", "P3"])

    # 1. P1 menjalankan internal event A1.
    sim.proses_internal("P1", "A1")
    # 2. P1 mengirim pesan m1 ke P2 melalui event A2.
    sim.kirim("P1", "A2", "m1", "P2")
    # 3. P2 menerima pesan m1 melalui event B1.
    sim.terima("P2", "B1", "m1")
    # 4. P2 menjalankan internal event B2.
    sim.proses_internal("P2", "B2")
    # 5. P2 mengirim pesan m2 ke P3 melalui event B3.
    sim.kirim("P2", "B3", "m2", "P3")
    # 6. P3 menerima pesan m2 melalui event C1.
    sim.terima("P3", "C1", "m2")
    # 7. P3 menjalankan internal event C2.
    sim.proses_internal("P3", "C2")
    # 8. P3 mengirim pesan m3 ke P1 melalui event C3.
    sim.kirim("P3", "C3", "m3", "P1")
    # 9. P1 menerima pesan m3 melalui event A3.
    sim.terima("P1", "A3", "m3")
    # 10. P1 menjalankan internal event A4.
    sim.proses_internal("P1", "A4")

    return sim


# =====================================================================
# BAGIAN 3: Menampilkan tabel hasil simulasi di terminal.
# =====================================================================


def tampilkan_tabel(sim):
    """Menampilkan log simulasi dalam bentuk tabel yang rapi."""
    judul = ["No", "Proses", "Event", "Jenis", "Pesan", "Timestamp", "Keterangan"]
    baris = []
    for e in sim.log:
        baris.append([str(e["no"]), e["proses"], e["event"], e["jenis"],
                      e["pesan"], str(e["ts"]), e["keterangan"]])

    # Hitung lebar maksimum tiap kolom agar tabel rapi.
    lebar = [len(j) for j in judul]
    for b in baris:
        for i, sel in enumerate(b):
            lebar[i] = max(lebar[i], len(sel))

    def garis_pemisah():
        return "+" + "+".join("-" * (w + 2) for w in lebar) + "+"

    def format_baris(sel):
        return "| " + " | ".join(s.ljust(lebar[i]) for i, s in enumerate(sel)) + " |"

    print(garis_pemisah())
    print(format_baris(judul))
    print(garis_pemisah())
    for b in baris:
        print(format_baris(b))
    print(garis_pemisah())


# =====================================================================
# BAGIAN 4: Verifikasi konsistensi hasil simulasi.
# =====================================================================


def bangun_relasi_happened_before(sim):
    """
    Membangun relasi happened-before (->) dari data event:
      1. Urutan program: event sebelumnya pada proses yang sama
         happened-before event berikutnya.
      2. Send -> Receive: send event yang mengirim pesan
         happened-before receive event penerima pesan tersebut.
    Mengembalikan himpunan pasangan (event_awal, event_akhir).
    """
    relasi = set()

    # Aturan 1: urutan program dalam satu proses.
    per_proses = defaultdict(list)
    for e in sim.log:
        per_proses[e["proses"]].append(e)
    for daftar in per_proses.values():
        for i in range(len(daftar)):
            for j in range(i + 1, len(daftar)):
                relasi.add((daftar[i]["event"], daftar[j]["event"]))

    # Aturan 2: send -> receive (berdasarkan pemetaan pesan).
    event_by_name = {e["event"]: e for e in sim.log}
    for e in sim.log:
        if e["jenis"] == "Receive":
            id_pesan = e["pesan"].split()[0]  # contoh: "m1 dari P1" -> "m1"
            pengirim, ts_send = sim.info_send[id_pesan]
            nama_send = next(x["event"] for x in sim.log
                             if x["proses"] == pengirim and x["ts"] == ts_send
                             and x["jenis"] == "Send")
            relasi.add((nama_send, e["event"]))

    return relasi, event_by_name


def verifikasi(sim):
    """
    Melakukan 4 pemeriksaan konsistensi:
      1. Timestamp tiap proses selalu meningkat.
      2. Timestamp receive > timestamp send yang sesuai.
      3. Jika A -> B (happened-before), maka ts(A) < ts(B).
      4. Ringkasan LULUS/GAGAL.
    """
    hasil = []

    # --- Pemeriksaan 1: timestamp meningkat pada setiap proses. ---
    oke1 = True
    detail1 = []
    per_proses = defaultdict(list)
    for e in sim.log:
        per_proses[e["proses"]].append(e)
    for proses, daftar in per_proses.items():
        for i in range(1, len(daftar)):
            if daftar[i]["ts"] <= daftar[i - 1]["ts"]:
                oke1 = False
                detail1.append(
                    f"{proses}: {daftar[i-1]['event']}({daftar[i-1]['ts']}) -> "
                    f"{daftar[i]['event']}({daftar[i]['ts']}) TIDAK MENINGKAT")
    if oke1:
        for proses, daftar in per_proses.items():
            urutan = ", ".join(f"{e['event']}={e['ts']}" for e in daftar)
            detail1.append(f"{proses}: {urutan}")
    hasil.append(("1. Timestamp meningkat pada setiap proses", oke1, detail1))

    # --- Pemeriksaan 2: ts(receive) > ts(send) untuk setiap pesan. ---
    oke2 = True
    detail2 = []
    for e in sim.log:
        if e["jenis"] == "Receive":
            id_pesan = e["pesan"].split()[0]
            pengirim, ts_send = sim.info_send[id_pesan]
            if e["ts"] <= ts_send:
                oke2 = False
                detail2.append(
                    f"{id_pesan}: ts(send)={ts_send} >= ts(receive)={e['ts']}")
            else:
                detail2.append(
                    f"{id_pesan}: ts(send {pengirim}) = {ts_send} < "
                    f"ts(receive {e['proses']}) = {e['ts']}")
    hasil.append(("2. Timestamp receive > timestamp send", oke2, detail2))

    # --- Pemeriksaan 3: A -> B maka ts(A) < ts(B). ---
    relasi, event_by_name = bangun_relasi_happened_before(sim)
    oke3 = True
    detail3 = []
    for a, b in sorted(relasi):
        ts_a = event_by_name[a]["ts"]
        ts_b = event_by_name[b]["ts"]
        if ts_a >= ts_b:
            oke3 = False
            detail3.append(f"{a} -> {b}: ts({a})={ts_a} >= ts({b})={ts_b}")
    if oke3:
        detail3.append(f"Seluruh {len(relasi)} pasangan relasi happened-before "
                       "memenuhi ts(A) < ts(B)")
    hasil.append(("3. Happened-before (A -> B) => ts(A) < ts(B)", oke3, detail3))

    # --- Pemeriksaan 4: ringkasan akhir. ---
    semua_lulus = all(oke for _, oke, _ in hasil)
    print("=" * 72)
    print("VERIFIKASI KONSISTENSI")
    print("=" * 72)
    for judul, oke, detail in hasil:
        status = "LULUS" if oke else "GAGAL"
        print(f"[{status}] {judul}")
        for d in detail:
            print(f"        - {d}")
        print()
    print("-" * 72)
    if semua_lulus:
        print("RINGKASAN: SELURUH PEMERIKSAAN LULUS.")
        print("Simulasi konsisten dengan aturan Lamport Timestamps.")
    else:
        print("RINGKASAN: TERDAPAT PEMERIKSAAN YANG GAGAL.")
    print("-" * 72)
    return semua_lulus


# =====================================================================
# BAGIAN 5: Program utama.
# =====================================================================


def main():
    print("=" * 72)
    print("SIMULASI LAMPORT TIMESTAMPS  --  3 Proses (P1, P2, P3)")
    print("=" * 72)
    print()
    print("Skenario simulasi (10 event):")
    print("  1. P1 internal A1        6. P3 receive m2 (C1)")
    print("  2. P1 send m1 -> P2 (A2) 7. P3 internal C2")
    print("  3. P2 receive m1 (B1)    8. P3 send m3 -> P1 (C3)")
    print("  4. P2 internal B2        9. P1 receive m3 (A3)")
    print("  5. P2 send m2 -> P3 (B3) 10. P1 internal A4")
    print()

    sim = jalankan_skenario()

    print("TABEL HASIL SIMULASI")
    tampilkan_tabel(sim)
    print()

    print("Logical clock akhir setiap proses:")
    for p, c in sim.clock.items():
        print(f"  {p} = {c}")
    print()

    verifikasi(sim)
    print()
    print("CATATAN PENTING:")
    print("  Timestamp Lamport yang lebih kecil menunjukkan urutan timestamp")
    print("  yang lebih awal dalam penomoran logis. Namun, timestamp yang")
    print("  lebih kecil TIDAK selalu membuktikan hubungan sebab-akibat")
    print("  (happened-before). Dua event yang tidak terkait (parallel)")
    print("  tetap bisa memiliki timestamp berbeda tanpa ada relasi")
    print("  sebab-akibat di antara keduanya.")


if __name__ == "__main__":
    main()
