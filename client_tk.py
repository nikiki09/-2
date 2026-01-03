import tkinter as tk
from tkinter import ttk, messagebox
import requests

BASE_URL = "http://127.0.0.1:8000/api"

# Палитра
COLORS = {
    "frame_bg": "#BB8588",   # рамка/внешние блоки
    "list_bg": "#EFEBCE",    # фон списка
    "btn_bg": "#EFEBCE",     # фон кнопок
    "done_row": "#D6CE93",   # выполнено
    "not_row": "#D8A48F",    # не выполнено
    "text_dark": "#1a1a1a",
    "text_light": "#ffffff",
    "placeholder": "#6b6b6b",
}

BTN_PADY = 10
ENTRY_IPADY = 10


def style_ttk(root: tk.Tk):
    s = ttk.Style(root)
    try:
        s.theme_use("clam")
    except Exception:
        pass

    s.configure(
        "Treeview",
        background=COLORS["list_bg"],
        fieldbackground=COLORS["list_bg"],
        foreground=COLORS["text_dark"],
        rowheight=30,
        borderwidth=0,
        relief="flat",
        highlightthickness=0,
    )
    s.configure(
        "Treeview.Heading",
        background=COLORS["frame_bg"],
        foreground=COLORS["text_light"],
        relief="flat",
        padding=(8, 6),
        font=("Segoe UI", 10, "bold"),
        borderwidth=0,
    )
    s.map(
        "Treeview",
        background=[("selected", COLORS["frame_bg"])],
        foreground=[("selected", COLORS["text_light"])],
    )

    s.configure(
        "TCombobox",
        padding=(6, 6),
        foreground=COLORS["text_dark"],
        fieldbackground=COLORS["btn_bg"],
        background=COLORS["btn_bg"],
        borderwidth=0,
        relief="flat",
    )


def make_button(parent, text, command):
    return tk.Button(
        parent,
        text=text,
        command=command,
        bg=COLORS["btn_bg"],
        fg=COLORS["text_dark"],
        activebackground=COLORS["btn_bg"],
        activeforeground=COLORS["text_dark"],
        relief="flat",
        bd=0,
        padx=14,
        pady=BTN_PADY,
        cursor="hand2",
        font=("Segoe UI", 10, "bold"),
    )


class HabitsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Трекер привычек")
        self.geometry("900x520")
        self.configure(bg=COLORS["frame_bg"])

        style_ttk(self)

        self.selected_habit_id = None

        top = tk.Frame(self, bg=COLORS["frame_bg"])
        top.pack(fill="x", padx=12, pady=(12, 8))

        self.search_var = tk.StringVar()
        self.entry_search = tk.Entry(
            top,
            textvariable=self.search_var,
            width=40,
            bg=COLORS["btn_bg"],
            fg=COLORS["placeholder"],
            insertbackground=COLORS["text_dark"],
            relief="flat",
            bd=0,
            font=("Segoe UI", 10),
        )
        self.entry_search.pack(side="left", padx=(0, 8), pady=0, ipady=ENTRY_IPADY)

        self._placeholder_text = "Поиск"
        self._placeholder_active = True
        self._set_placeholder()

        self.entry_search.bind("<FocusIn>", self._on_search_focus_in)
        self.entry_search.bind("<FocusOut>", self._on_search_focus_out)
        self.entry_search.bind("<Return>", lambda e: self.refresh())

        self.btn_search = make_button(top, "Найти", self.refresh)
        self.btn_search.pack(side="left", padx=(0, 8), pady=0)

        self.btn_clear = make_button(top, "Очистить", self.clear_search)
        self.btn_clear.pack(side="left", padx=(0, 8), pady=0)

        self.btn_refresh = make_button(top, "Обновить", self.refresh)
        self.btn_refresh.pack(side="right", padx=0, pady=0)

        middle = tk.Frame(self, bg=COLORS["frame_bg"])
        middle.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        inner = tk.Frame(middle, bg=COLORS["frame_bg"])
        inner.pack(fill="both", expand=True, padx=4, pady=4)

        columns = ("name", "frequency", "done_today")
        self.tree = ttk.Treeview(inner, columns=columns, show="headings", height=14)

        self.tree.heading("name", text="Привычка")
        self.tree.heading("frequency", text="Частота")
        self.tree.heading("done_today", text="Сделано сегодня")

        self.tree.column("name", width=560, anchor="w")
        self.tree.column("frequency", width=160, anchor="center")
        self.tree.column("done_today", width=160, anchor="center")

        self.tree.tag_configure("done", background=COLORS["done_row"], foreground=COLORS["text_light"])
        self.tree.tag_configure("not_done", background=COLORS["not_row"], foreground=COLORS["text_light"])

        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-1>", self._tree_click, add="+")

        self.tree.pack(fill="both", expand=True, padx=0, pady=0)

        bottom = tk.Frame(self, bg=COLORS["frame_bg"])
        bottom.pack(fill="x", padx=12, pady=(0, 12))

        actions = tk.Frame(bottom, bg=COLORS["frame_bg"])
        actions.pack(side="left", padx=0, pady=0)

        self.btn_add = make_button(actions, "Добавить", self.open_add_window)
        self.btn_done = make_button(actions, "Выполнено сегодня", self.mark_done_today)
        self.btn_undone = make_button(actions, "Отменить сегодня", self.unmark_done_today)
        self.btn_stats = make_button(actions, "Статистика", self.show_stats)
        self.btn_delete = make_button(actions, "Удалить", self.delete_habit)

        self.btn_add.pack(side="left", padx=6, pady=0)
        self.btn_done.pack(side="left", padx=6, pady=0)
        self.btn_undone.pack(side="left", padx=6, pady=0)
        self.btn_stats.pack(side="left", padx=6, pady=0)
        self.btn_delete.pack(side="left", padx=6, pady=0)

        self.status = tk.Label(
            bottom,
            text="Готово",
            bg=COLORS["frame_bg"],
            fg=COLORS["text_light"],
            anchor="e",
            font=("Segoe UI", 10),
        )
        self.status.pack(side="right", fill="x", expand=True, padx=(12, 0), pady=0)

        self.bind_all("<Button-1>", self._global_click_strict, add="+")

        self.update_action_buttons()
        self.refresh()

    def _is_descendant(self, widget, ancestor) -> bool:
        w = widget
        while w is not None:
            if w == ancestor:
                return True
            w = getattr(w, "master", None)
        return False

    def _global_click_strict(self, event):
        w = self.winfo_containing(event.x_root, event.y_root)
        if w is None:
            return

        if self._is_descendant(w, self.tree):
            return

        self.tree.selection_remove(self.tree.selection())
        self.update_action_buttons()

    def _set_placeholder(self):
        self.search_var.set(self._placeholder_text)
        self.entry_search.config(fg=COLORS["placeholder"])
        self._placeholder_active = True

    def _clear_placeholder(self):
        self.search_var.set("")
        self.entry_search.config(fg=COLORS["text_dark"])
        self._placeholder_active = False

    def _on_search_focus_in(self, event=None):
        if self._placeholder_active:
            self._clear_placeholder()

    def _on_search_focus_out(self, event=None):
        if not self.search_var.get().strip():
            self._set_placeholder()

    def _get_search_query(self) -> str:
        if self._placeholder_active:
            return ""
        return self.search_var.get().strip()

    def set_status(self, text: str):
        self.status.config(text=text)

    def clear_search(self):
        self._set_placeholder()
        self.refresh()

    def update_action_buttons(self):
        state = "normal" if self.selected_habit_id else "disabled"
        for b in (self.btn_done, self.btn_undone, self.btn_stats, self.btn_delete):
            b.config(state=state)
            b.config(cursor="hand2" if state == "normal" else "arrow")

    def on_select(self, event=None):
        sel = self.tree.selection()
        if not sel:
            return
        self.selected_habit_id = int(sel[0])
        self.update_action_buttons()

    def on_double_click(self, event=None):
        if self.selected_habit_id:
            self.mark_done_today()

    def _tree_click(self, event):
        row_id = self.tree.identify_row(event.y)
        if not row_id:
            self.tree.selection_remove(self.tree.selection())
            self.selected_habit_id = None
            self.update_action_buttons()

    def refresh(self):
        q = self._get_search_query()

        try:
            url = f"{BASE_URL}/habits/"
            if q:
                url = f"{BASE_URL}/habits/?q={requests.utils.quote(q)}"
            r = requests.get(url, timeout=5)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить список привычек.\n\n{e}")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        habits = data.get("habits", [])
        done_count = 0

        for h in habits:
            habit_id = h["id"]
            freq = "ежедневно" if h.get("frequency") == "daily" else "еженедельно"
            done_today = bool(h.get("done_today"))
            done_text = "да" if done_today else "нет"
            tag = "done" if done_today else "not_done"
            if done_today:
                done_count += 1

            self.tree.insert("", "end", iid=str(habit_id), values=(h["name"], freq, done_text), tags=(tag,))

        self.tree.selection_remove(self.tree.selection())
        self.selected_habit_id = None
        self.update_action_buttons()
        self.set_status(f"Привычек: {len(habits)} | Сделано сегодня: {done_count}")

    def open_add_window(self):
        AddHabitWindow(self, on_saved=self.refresh)

    def mark_done_today(self):
        if not self.selected_habit_id:
            return

        try:
            r = requests.post(f"{BASE_URL}/habits/{self.selected_habit_id}/done/", timeout=5)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отметить выполнение.\n\n{e}")
            return

        if data.get("created") is True:
            messagebox.showinfo("Готово", "Отмечено: выполнено сегодня.")
        else:
            messagebox.showinfo("Готово", "Сегодня уже было отмечено ранее.")

        self.refresh()

    def unmark_done_today(self):
        if not self.selected_habit_id:
            return

        try:
            r = requests.post(f"{BASE_URL}/habits/{self.selected_habit_id}/undone/", timeout=5)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось отменить выполнение.\n\n{e}")
            return

        if data.get("deleted", 0) > 0:
            messagebox.showinfo("Готово", "Отметка за сегодня отменена.")
        else:
            messagebox.showinfo("Готово", "На сегодня отметки не было.")

        self.refresh()

    def show_stats(self):
        if not self.selected_habit_id:
            return

        try:
            r = requests.get(f"{BASE_URL}/habits/{self.selected_habit_id}/stats/", timeout=5)
            r.raise_for_status()
            data = r.json()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось получить статистику.\n\n{e}")
            return

        name = data.get("name", "")
        total = data.get("total_done", 0)
        messagebox.showinfo("Статистика", f"Привычка: {name}\nВсего выполнений: {total}")

    def delete_habit(self):
        if not self.selected_habit_id:
            return

        if not messagebox.askyesno("Подтверждение", "Удалить выбранную привычку?"):
            return

        try:
            r = requests.delete(f"{BASE_URL}/habits/{self.selected_habit_id}/delete/", timeout=5)
            r.raise_for_status()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить привычку.\n\n{e}")
            return

        messagebox.showinfo("Готово", "Привычка удалена.")
        self.refresh()


class AddHabitWindow(tk.Toplevel):
    def __init__(self, master: HabitsApp, on_saved):
        super().__init__(master)
        self.title("Добавить привычку")
        self.geometry("440x240")
        self.resizable(False, False)
        self.on_saved = on_saved

        self.configure(bg=COLORS["frame_bg"])

        card = tk.Frame(self, bg=COLORS["frame_bg"])
        card.pack(fill="both", expand=True, padx=12, pady=12)

        tk.Label(
            card,
            text="Название привычки",
            bg=COLORS["frame_bg"],
            fg=COLORS["text_light"],
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 4))

        self.entry_name = tk.Entry(
            card,
            bg=COLORS["btn_bg"],
            fg=COLORS["text_dark"],
            insertbackground=COLORS["text_dark"],
            relief="flat",
            bd=0,
            font=("Segoe UI", 10),
        )
        self.entry_name.pack(fill="x", padx=12, ipady=ENTRY_IPADY)

        tk.Label(
            card,
            text="Частота",
            bg=COLORS["frame_bg"],
            fg=COLORS["text_light"],
            font=("Segoe UI", 10, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 4))

        self.freq_ru_var = tk.StringVar(value="ежедневно")
        self.combo = ttk.Combobox(
            card,
            textvariable=self.freq_ru_var,
            values=["ежедневно", "еженедельно"],
            state="readonly",
        )
        self.combo.pack(fill="x", padx=12)

        btn_frame = tk.Frame(card, bg=COLORS["frame_bg"])
        btn_frame.pack(fill="x", padx=12, pady=16)

        make_button(btn_frame, "Сохранить", self.save).pack(side="left", padx=5)
        make_button(btn_frame, "Отмена", self.destroy).pack(side="left", padx=5)

        self.entry_name.focus()

    def save(self):
        name = self.entry_name.get().strip()
        freq_ru = self.freq_ru_var.get().strip()

        if not name:
            messagebox.showwarning("Внимание", "Название не может быть пустым.")
            return

        frequency = "daily" if freq_ru == "ежедневно" else "weekly"

        try:
            r = requests.post(
                f"{BASE_URL}/habits/create/",
                json={"name": name, "frequency": frequency},
                timeout=5,
            )
            r.raise_for_status()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать привычку.\n\n{e}")
            return

        messagebox.showinfo("Готово", "Привычка добавлена.")
        self.destroy()
        self.on_saved()


if __name__ == "__main__":
    app = HabitsApp()
    app.mainloop()
