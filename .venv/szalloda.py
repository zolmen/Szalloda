import tkinter as tk
from tkinter import simpledialog, messagebox
from abc import ABC, abstractmethod
from datetime import datetime

class Szoba(ABC):
    def __init__(self, szobaszam, ar):
        self.szobaszam = szobaszam
        self.ar = ar

class EgyagyasSzoba(Szoba):
    def __init__(self, szobaszam):
        super().__init__(szobaszam, 5000)

class KetagyasSzoba(Szoba):
    def __init__(self, szobaszam):
        super().__init__(szobaszam, 8000)

class Szalloda:
    def __init__(self, nev):
        self.nev = nev
        self.szobak = {}
        self.foglalasok = {}

    def foglal(self, szobaszam, datum):
        if datum in self.foglalasok and szobaszam in self.foglalasok[datum]:
            return None
        self.foglalasok.setdefault(datum, []).append(szobaszam)
        return self.szobak[szobaszam].ar

    def foglalas_lemondasa(self, szobaszam, datum):
        if datum in self.foglalasok and szobaszam in self.foglalasok[datum]:
            self.foglalasok[datum].remove(szobaszam)
            if not self.foglalasok[datum]:
                del self.foglalasok[datum]
            return True
        return False

    def foglalasok_listazasa(self):
        return self.foglalasok

class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title=None, prompt=None):
        self.prompt = prompt
        super().__init__(parent, title)

    def body(self, master):
        self.geometry('200x150')
        self.resizable(False, False)
        tk.Label(master, text=self.prompt).pack(pady=10)
        self.entry = tk.Entry(master)
        self.entry.pack(pady=10)
        return self.entry

    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(box, text="OK", width=10, command=self.ok).pack(side=tk.LEFT, padx=5, pady=5)
        tk.Button(box, text="Mégse", width=10, command=self.cancel).pack(side=tk.LEFT, padx=5, pady=5)
        box.pack()

    def ok(self):
        self.result = self.entry.get()
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

class FoglaltsagDialog(simpledialog.Dialog):
    def __init__(self, parent, title, foglalasok):
        self.foglalasok = foglalasok
        super().__init__(parent, title)

    def body(self, master):
        self.geometry('300x200')
        self.resizable(False, False)
        if self.foglalasok:
            foglalasok_szoveg = "\n".join(f"{datum}: {szobak}" for datum, szobak in self.foglalasok.items())
        else:
            foglalasok_szoveg = "Nincsenek foglalások."
        self.label = tk.Label(master, text=foglalasok_szoveg)
        self.label.pack(pady=10, padx=10)

    def buttonbox(self):
        box = tk.Frame(self)
        tk.Button(box, text="OK", width=10, command=self.ok).pack(side=tk.LEFT, padx=5, pady=5)
        box.pack()

    def ok(self):
        self.destroy()

class Application(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Szálloda foglalási rendszer')
        self.geometry('400x350')
        self.resizable(False, False)
        self.szalloda = Szalloda("Példa Szálloda")
        self.szalloda.szobak[101] = EgyagyasSzoba(101)
        self.szalloda.szobak[102] = EgyagyasSzoba(102)
        self.szalloda.szobak[103] = KetagyasSzoba(103)
        self.szalloda.szobak[104] = KetagyasSzoba(104)
        self.create_widgets()

    def create_widgets(self):
        self.center_frame = tk.Frame(self)  # Létrehozunk egy középső keretet
        self.center_frame.place(relx=0.5, rely=0.4, anchor='center')  # Középre helyezzük a keretet

        self.label = tk.Label(self.center_frame, text="Válasszon műveletet:")
        self.label.pack(pady=10)
        self.szoba_tipus_button = tk.Button(self.center_frame, text="Szobák és árak", command=self.szoba_tipusok)
        self.szoba_tipus_button.pack(pady=5)
        self.foglalas_button = tk.Button(self.center_frame, text="Foglalás",
                                         command=lambda: self.action_wrapper("Foglalás"))
        self.foglalas_button.pack(pady=5)
        self.lemondas_button = tk.Button(self.center_frame, text="Lemondás",
                                         command=lambda: self.action_wrapper("Lemondás"))
        self.lemondas_button.pack(pady=5)
        self.foglaltsag_button = tk.Button(self.center_frame, text="Foglaltság", command=self.show_foglaltsag)
        self.foglaltsag_button.pack(pady=5)

    def szoba_tipusok(self):
        szoba_info = "\n".join(f"Szoba {sz} - {type(self.szalloda.szobak[sz]).__name__}: {self.szalloda.szobak[sz].ar} Ft" for sz in sorted(self.szalloda.szobak))
        messagebox.showinfo("Szobák és árak", szoba_info)

    def action_wrapper(self, action_type):
        self.update_idletasks()
        self.title(f'{self.szalloda.nev} - {action_type}')
        datum = CustomDialog(self, title=action_type, prompt="Adja meg a dátumot (éééé-hh-nn):").result
        if not datum:
            return
        try:
            parsed_date = datetime.strptime(datum, "%Y-%m-%d").date()
            if parsed_date < datetime.today().date():
                messagebox.showerror("Hiba", "A megadott dátum a múltban van.")
                return
        except ValueError:
            messagebox.showerror("Hiba", "Érvénytelen dátumformátum.")
            return
        szobaszam = CustomDialog(self, title=action_type, prompt="Adja meg a szobaszámot:").result
        if not szobaszam or not szobaszam.isdigit() or int(szobaszam) not in self.szalloda.szobak:
            messagebox.showerror("Hiba", "Nincs ilyen szobaszám.")
            return
        szobaszam = int(szobaszam)
        if action_type == "Foglalás":
            ar = self.szalloda.foglal(szobaszam, parsed_date)
            if ar is None:
                messagebox.showinfo("Foglalás", "A szoba már foglalt ezen a napon.")
            else:
                messagebox.showinfo("Foglalás", f"A foglalás sikeres. Az ára: {ar} Ft")
        elif action_type == "Lemondás":
            if self.szalloda.foglalas_lemondasa(szobaszam, parsed_date):
                messagebox.showinfo("Lemondás", "A foglalás lemondva.")
            else:
                messagebox.showerror("Lemondás", "Nincs ilyen foglalás vagy már lemondva.")

    def show_foglaltsag(self):
        foglalasok = self.szalloda.foglalasok_listazasa()
        FoglaltsagDialog(self, title="Foglaltság", foglalasok=foglalasok)

if __name__ == "__main__":
    app = Application()
    app.mainloop()
