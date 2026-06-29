import tkinter as tk
import tkinter.font as tkfont
import tkinter.ttk as ttk
import os
import threading
import platform

MINT = "#3EB489"
BLACK = "#000000"

def perform_action(action: str):
    system = platform.system()
    if system == "Windows":
        if action == "shutdown":
            cmd = "shutdown /s /t 0"
        elif action == "restart":
            cmd = "shutdown /r /t 0"
        else:
            cmd = "rundll32.exe powrprof.dll,SetSuspendState 0,1,0"
    else:
        if action == "shutdown":
            cmd = "shutdown -h now"
        elif action == "restart":
            cmd = "shutdown -r now"
        else:
            cmd = "systemctl suspend" if system=="Linux" else "pmset sleepnow"
    os.system(cmd)

class CountdownApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.geometry("640x360")
        self.title("예약 종료/재시작/절전 타이머")
        self.configure(bg=BLACK)

        # ── Combobox 전용 스타일 정의 ──
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('My.TCombobox',
                        fieldbackground=BLACK,
                        background=BLACK,
                        foreground='white')
        style.map('My.TCombobox',
                  fieldbackground=[('readonly', BLACK)],
                  foreground=[('readonly', 'white')])

        # 3×3 그리드로 중앙 셀만 고정
        for i in (0,2):
            self.grid_rowconfigure(i, weight=1)
            self.grid_columnconfigure(i, weight=1)

        self.main_frame = tk.Frame(self, bg=BLACK)
        self.main_frame.grid(row=1, column=1)

        # 폰트 정의
        self.lbl_font   = tkfont.Font(family="Consolas", size=40)
        self.entry_font = tkfont.Font(family="Consolas", size=14)
        self.btn_font   = tkfont.Font(family="Consolas", size=12)
        self.radio_font = tkfont.Font(family="Consolas", size=12)
        self.pct_font   = tkfont.Font(family="Consolas", size=12)

        # 시간 선택 콤보박스 (시:0~1000, 분/초:0~59)
        frm = tk.Frame(self.main_frame, bg=BLACK)
        frm.pack(pady=5)
        self.h_var = tk.StringVar(value="0")
        self.m_var = tk.StringVar(value="0")
        self.s_var = tk.StringVar(value="0")
        self.entries = []

        hours = [str(i) for i in range(0,1001)]
        mins_secs = [str(i) for i in range(0,60)]

        for txt, var, vals in [("시", self.h_var, hours),
                               ("분", self.m_var, mins_secs),
                               ("초", self.s_var, mins_secs)]:
            cb = ttk.Combobox(frm,
                              style="My.TCombobox",
                              width=3,
                              textvariable=var,
                              values=vals,
                              font=self.entry_font,
                              justify="center",
                              state="readonly")
            cb.pack(side="left", padx=5)
            self.entries.append(cb)
            tk.Label(frm, text=txt, bg=BLACK, fg="white",
                     font=self.entry_font).pack(side="left")

        # 동작 선택 라디오
        self.action_var = tk.StringVar(value="shutdown")
        act_frm = tk.Frame(self.main_frame, bg=BLACK)
        act_frm.pack(pady=5)
        for val, label in [("shutdown","종료"),("restart","재시작"),("suspend","절전")]:
            tk.Radiobutton(
                act_frm, text=label, value=val, variable=self.action_var,
                bg=BLACK, fg="white", selectcolor=BLACK,
                activebackground=BLACK, activeforeground=MINT,
                font=self.radio_font
            ).pack(side="left", padx=10)

        # 타이머 라벨
        self.lbl = tk.Label(
            self.main_frame, text="00:00:00",
            bg=BLACK, fg=MINT, font=self.lbl_font
        )
        self.lbl.pack(pady=10)

        # 진행 바 + 퍼센트 텍스트
        self.canvas = tk.Canvas(self.main_frame, bg=BLACK, highlightthickness=0)
        self.canvas.pack(pady=10)
        self.bar = self.canvas.create_rectangle(0,0,0,0, fill=MINT, width=0)
        self.pct_text = self.canvas.create_text(0, 0, text="",
                                                fill=MINT, font=self.pct_font,
                                                anchor="w")

        # 버튼들 (Start, Pause, Resume, Stop, 사용 방법)
        btn_frm = tk.Frame(self.main_frame, bg=BLACK)
        btn_frm.pack(pady=5)

        btn_specs = [
            ("Start",   self.start),
            ("Pause",   self.pause),
            ("Resume",  self.resume),
            ("Stop",    self.stop),
            ("사용 방법", self.show_usage)
        ]
        for txt, cmd in btn_specs:
            tk.Button(
                btn_frm, text=txt, command=cmd,
                bg="#222", fg="white", activebackground=MINT,
                font=self.btn_font
            ).pack(side="left", padx=5)

        # 리사이즈 기준 저장
        self.update_idletasks()
        self.base_w        = self.winfo_width()
        self.base_h        = self.winfo_height()
        self.base_lbl_sz   = self.lbl_font['size']
        self.base_entry_sz = self.entry_font['size']
        self.base_btn_sz   = self.btn_font['size']
        self.base_rad_sz   = self.radio_font['size']
        self.base_pct_sz   = self.pct_font['size']
        self.base_ent_w    = self.entries[0]['width']

        self.bind("<Configure>", self._on_resize)

        # 타이머 상태 변수
        self.total_seconds = 0
        self.remaining     = 0
        self._job          = None
        self.paused        = False

    def _on_resize(self, event):
        if event.widget is not self: return
        w, h = event.width, event.height
        sx, sy = w/self.base_w, h/self.base_h

        # 폰트 크기 조정
        self.lbl_font.configure(size=max(8, int(self.base_lbl_sz*sy)))
        self.entry_font.configure(size=max(6, int(self.base_entry_sz*sy)))
        self.btn_font.configure(size=max(6, int(self.base_btn_sz*sy)))
        self.radio_font.configure(size=max(6, int(self.base_rad_sz*sy)))
        self.pct_font.configure(size=max(6, int(self.base_pct_sz*sy)))

        # 콤보박스 폭
        new_w = max(1, int(self.base_ent_w*sx))
        for cb in self.entries:
            cb.config(width=new_w)

        # 진행 바 크기
        self.canvas.config(width=int(w*0.8), height=max(5, int(h*0.02)))

    def start(self):
        if self._job:
            self.after_cancel(self._job)
        try:
            h, m, s = map(int, (self.h_var.get(), self.m_var.get(), self.s_var.get()))
        except ValueError:
            return
        self.total_seconds = h*3600 + m*60 + s
        if self.total_seconds <= 0: return
        self.remaining = self.total_seconds
        self.paused    = False
        self._tick()

    def _tick(self):
        if self.paused: return

        h, rem = divmod(self.remaining, 3600)
        mm, ss = divmod(rem, 60)
        self.lbl.config(text=f"{h:02d}:{mm:02d}:{ss:02d}")

        cw = self.canvas.winfo_width()
        filled = (self.total_seconds - self.remaining)/self.total_seconds * cw
        self.canvas.coords(self.bar, 0,0, filled, self.canvas.winfo_height())

        pct = self.remaining/self.total_seconds * 100
        x, y = filled+5, self.canvas.winfo_height()/2
        self.canvas.coords(self.pct_text, x, y)
        self.canvas.itemconfig(self.pct_text, text=f"{pct:5.1f}%")

        if self.remaining <= 0:
            threading.Thread(target=perform_action,
                             args=(self.action_var.get(),),
                             daemon=True).start()
            return

        self.remaining -= 1
        self._job = self.after(1000, self._tick)

    def pause(self):
        self.paused = True
        if self._job: self.after_cancel(self._job)

    def resume(self):
        if self.paused and self.remaining>0:
            self.paused = False
            self._tick()

    def stop(self):
        self.paused = True
        if self._job: self.after_cancel(self._job)
        self.remaining = 0
        self.lbl.config(text="00:00:00")
        self.canvas.coords(self.bar, 0,0,0, self.canvas.winfo_height())
        self.canvas.itemconfig(self.pct_text, text="")

    def show_usage(self):
        """반투명 Toplevel 창에 사용법 표시"""
        # 이미 열려 있으면 포커스만
        if hasattr(self, 'help_win') and self.help_win.winfo_exists():
            self.help_win.lift()
            return

        self.help_win = tk.Toplevel(self)
        self.help_win.title("사용 방법")
        # 반투명 & 항상 위
        self.help_win.attributes("-alpha", 0.9)
        self.help_win.attributes("-topmost", True)
        # 본창 크기와 위치에 맞춤
        x, y = self.winfo_rootx(), self.winfo_rooty()
        w, h = self.winfo_width(), self.winfo_height()
        self.help_win.geometry(f"{w}x{h}+{x}+{y}")
        self.help_win.configure(bg=BLACK)

        help_text = (
            "1. 시/분/초 콤보박스에서 원하는 시간을 선택하세요.\n"
            "   시,분,초는 마우스 드래그 또는 선택으로 변경할 수 있습니다\n"
            "   초/분이 60 이상이 될 경우 각각 분/시간이 1씩 추가됩니다.\n"
            "2. 동작(종료/재시작/절전)을 선택합니다.\n"
            "3. Start 버튼을 눌러 타이머를 시작합니다.\n"
            "4. Pause→일시정지, Resume→재개, Stop→초기화\n"
            "5. 도움말 창을 닫으려면 창 안을 클릭하거나 ESC키를 누르세요."
        )
        lbl = tk.Label(self.help_win, text=help_text, justify="left",
                       bg=BLACK, fg="white", font=self.entry_font)
        lbl.pack(padx=20, pady=20)

        # 클릭 또는 ESC로 닫기
        self.help_win.bind("<Button-1>", lambda e: self.help_win.destroy())
        self.help_win.bind("<Escape>",  lambda e: self.help_win.destroy())

if __name__ == "__main__":
    app = CountdownApp()
    app.mainloop()
