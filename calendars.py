""" Widgets principales del tkcalendar"""
import tkinter as tk
from tkcalendar import *
from datetime import date

class CalendarField(tk.Frame):
    def __init__(self, master, label="Fecha de cita: ", date_pattern='yyyy-mm-dd', **kwargs):
        super().__init__(master, **kwargs)
        self._label = tk.Label(self, text=label)
        self._label.pack(side="left", padx=(0,8))

        self.entry = DateEntry(self,
                               date_pattern=date_pattern,
                               background='lightblue',
                               foreground='black',
                               borderwidth=2,
                               )
        self.entry.pack(side="left", fill="x", expand=True)

    def get(self):
        return self.entry.get_date()

    def get_text(self):
        return self.entry.get()

    def set(self,d):
        if isinstance(d, date):
            self.entry.set_date(d)
        else:
            self.entry.set_date(d)