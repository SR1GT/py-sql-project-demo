import pymysql
import base64
import time
import calendar

from tkinter import *
from tkinter import messagebox, font
from tkinter.ttk import Treeview, Combobox


class App:
    # region 全局变量
    # region 自定义数据
    background_color = "#1e863f"  # 主界面背景颜色
    dbUsr = "root"  # 数据库管理员账号
    dbPwd = "root"  # 数据库管理员密码
    database = "design"  # 数据库名称
    systemName = "机场航班起降与协调调度"
    # endregion

    # region 数据库名称
    us = "User_Set"  # 用户表
    fis = "Flight_info_show"  # 航班信息表
    gi = "Ground_Info"  # 跑道情况表
    ctc = "CT_Control"  # 塔台调度表
    fc = "Fli_Control"  # 航班调度表
    # endregion

    # region 数据库操作变量
    db = None
    cursor = None
    # endregion

    # region 各库属性
    us_col = ("Uno", "Password", "Username", "Identy")
    fis_col = ("Fno", "Fli_range", "Fli_date", "Fli_state", "Fli_type")
    gi_col = ("G_number", "Gno", "G_info", "G_worker")
    ctc_col = ("Cno", "Cname", "C_worker")
    fc_col = ("Cno", "Fno", "G_number")
    columns = {us: us_col, fis: fis_col, gi: gi_col, ctc: ctc_col, fc: fc_col}
    # endregion

    # region 当前用户信息
    username = None
    name = None
    identy = None
    # endregion

    # 专用数据
    tree = None

    # endregion

    def __init__(self):
        self.window = Tk()
        self.window.title(f"{self.systemName}系统")
        self.window.geometry("800x600")
        # 居中显示
        # self.window.geometry("%dx%d+%d+%d" % (800, 600, (self.window.winfo_screenwidth())/2,
        #                                       (self.window. winfo_screenheight())/2))
        # 设置窗口不可拉伸
        self.window.resizable(False, False)
        # 设置窗口背景颜色
        self.window.config(background=self.background_color)
        # 置顶显示
        # self.window.attributes("-topmost", True)
        # 设置全局字体
        self.window.defaultFont = font.nametofont("TkDefaultFont")
        self.window.defaultFont.config(family="Times New Roman", size=14, weight=font.BOLD)

        label_cr = Label(self.window, text="            ", bg=self.background_color)

        def cr(events):
            print(events)
            messagebox.showinfo("提示", "绵延不绝，亘古永恒\nCopyright © 2023 王新阳, Inc. All rights reserved")

        label_cr.bind("<Button-1>", cr)
        label_cr.pack(side='bottom')
        # 创建用户界面
        self.frame_login = Frame(self.window, bg=self.background_color)
        self.frame_welcome = Frame(self.window, bg=self.background_color)
        self.content = StringVar()
        Label(self.frame_welcome, bg=self.background_color, text=f"欢迎使用{self.systemName}系统",
              font=("黑体", 20)).pack(pady=20)
        Label(self.frame_welcome, textvariable=self.content, bg=self.background_color).pack()
        # 连接至数据库
        self.connect2database()
        # 关闭窗口
        self.window.protocol("WM_DELETE_WINDOW", self.onClose)
        # 开启窗口
        self.window.mainloop()

    # region GUI

    # region 绘表

    # 航班信息表
    def table_fis(self, window):
        datas = self.onSelect('*', self.fis, None, None)
        cols = self.fis_col
        tree = Treeview(window)
        tree["show"] = "headings"
        tree["columns"] = cols
        for i in range(0, 5):
            tree.column(cols[i], width=100)
        tree.heading(cols[0], text="航班号")
        tree.heading(cols[1], text="起降地")
        tree.heading(cols[2], text="起降时间")
        tree.heading(cols[3], text="航班状态")
        tree.heading(cols[4], text="机型")
        for i, row in enumerate(datas):
            tree.insert("", i + 1, text=str(i), values=row)
        return tree

    # 跑道情况表
    def table_gi(self, window):
        datas = self.onSelect('*', self.gi, None, None)
        cols = self.gi_col
        tree = Treeview(window)
        tree["show"] = "headings"
        tree["columns"] = cols
        for i in range(0, 4):
            tree.column(cols[i], width=150)
        tree.heading(cols[0], text="情况编号")
        tree.heading(cols[1], text="跑道号")
        tree.heading(cols[2], text="跑道情况")
        tree.heading(cols[3], text="负责人")
        for i, row in enumerate(datas):
            tree.insert("", i + 1, text=str(i), values=row)
        return tree

    # 塔台调度表
    def table_ctc(self, window):
        datas = self.onSelect('*', self.ctc, None, None)
        cols = self.ctc_col
        tree = Treeview(window)
        tree["show"] = "headings"
        tree["columns"] = cols
        for i in range(0, 3):
            tree.column(cols[i], width=150)
        tree.heading(cols[0], text="指令编号")
        tree.heading(cols[1], text="指令内容")
        tree.heading(cols[2], text="负责人")
        for i, row in enumerate(datas):
            tree.insert("", i + 1, text=str(i), values=row)
        return tree

    # endregion

    # 用户登录/注册/修改密码窗口
    def window_user(self):
        def login():
            # 登录
            if entry_un.get() == '' or entry_pw.get() == '':
                messagebox.showerror("错误", "账号或密码为空")
                return
            datas = (entry_un.get(), None, None, None)
            info = self.onSelect('*', self.us, datas, None)
            if info is not None:
                if info == ():
                    messagebox.showerror("错误", "账号不存在")
                else:
                    info = info[0]
                    un_sel = info[0]
                    pw_sel = info[1]
                    if un_sel == entry_un.get() and pw_sel.encode("utf-8") == base64.b64encode(
                            entry_pw.get().encode("utf-8")):
                        name = info[2]
                        status = int(info[3])
                        entry_un.delete(0, END)
                        entry_pw.delete(0, END)
                        entry_un.focus_set()
                        if 0 < status < 6:
                            self.username = un_sel
                            self.identy = status
                            self.name = name
                            self.frame_login.pack_forget()
                            self.content.set(f"欢迎 {self.name if '' else self.username}")
                            self.frame_welcome.pack(expand=1)
                            if status == 1:
                                # 旅客窗口
                                self.traveller()
                            elif status == 2:
                                # 地勤窗口
                                self.ground()
                            elif status == 3:
                                # 塔台窗口
                                self.tower()
                            elif status == 4:
                                # 机场管理员窗口
                                self.admin()
                            elif status == 5:
                                # 超级管理员窗口
                                self.root()
                        else:
                            messagebox.showerror("错误", "用户身份错误")
                    else:
                        messagebox.showerror("错误", "账号或密码错误")
            else:
                messagebox.showerror("错误", "出现错误 None, 登录失败")

        def signin():
            # 注册
            def submit():
                if entry_un_new.get() == '' or entry_pw_new.get() == '':
                    messagebox.showerror("错误", "提交内容不能为空")
                elif entry_pw_new.get() != entry_pw_again.get():
                    messagebox.showerror("错误", "两次输入密码不一致")
                else:
                    info = self.onSelect('*', self.us, (entry_un_new.get(), None, None, None), None)
                    if info is not None:
                        if info == ():
                            code = entry_code.get()
                            if code == '':
                                self.onInsert(self.us, [(entry_un_new.get(),
                                                         base64.b64encode(entry_pw_new.get().encode('utf-8')),
                                                         '', "1")])
                                messagebox.showinfo("提示", "旅客注册")
                                back()
                            else:
                                name = entry_name.get()
                                if name == '':
                                    messagebox.showerror("错误", "姓名不能为空")
                                else:
                                    if code == 'gc':
                                        try:
                                            job_number = int(entry_un_new.get())
                                            if 1000 < job_number < 10000:
                                                self.onInsert(self.us, [(
                                                    entry_un_new.get(),
                                                    base64.b64encode(entry_pw_new.get().encode('utf-8')),
                                                    entry_name.get(), "2")])
                                                messagebox.showinfo("提示", "地勤注册")
                                                back()
                                            else:
                                                messagebox.showerror("错误", "工号超出范围")
                                        except ValueError:
                                            messagebox.showerror("错误", "工号格式不正确")
                                    elif code == 'tc':
                                        try:
                                            job_number = int(entry_un_new.get())
                                            if 1000 < job_number < 10000:
                                                self.onInsert(self.us, [(
                                                    entry_un_new.get(), base64.b64encode(entry_pw_new.get().encode('utf-8')),
                                                    entry_name.get(), "3")])
                                                messagebox.showinfo("提示", "塔台注册")
                                            else:
                                                messagebox.showerror("错误", "工号超出范围")
                                        except ValueError:
                                            messagebox.showerror("错误", "工号格式不正确")
                                        back()
                                    elif code == 'admin':
                                        self.onInsert(self.us, [(
                                            entry_un_new.get(), base64.b64encode(entry_pw_new.get().encode('utf-8')),
                                            entry_name.get(), "4")])
                                        messagebox.showinfo("提示", "管理员注册")
                                        back()
                                    else:
                                        messagebox.showerror("错误", "身份码错误")
                        else:
                            messagebox.showerror("错误", f"账号{entry_un_new.get()}已存在")
                    else:
                        messagebox.showerror("错误", "出现错误 None, 注册失败")

            def back():
                frame_signin.pack_forget()
                self.frame_login.pack(expand=1)

            self.frame_login.pack_forget()
            frame_signin = Frame(self.window, bg=self.background_color)
            frame_signin.pack(expand=1)
            Label(frame_signin, bg=self.background_color, text="  用  户  注  册", font=("黑体", 20)).pack(pady=20)
            frame_signin_form = Frame(frame_signin, bg=self.background_color)
            frame_signin_form.pack()
            Label(frame_signin_form, bg=self.background_color, text="账号").grid(row=0, column=0, pady=10, padx=5)
            Label(frame_signin_form, bg=self.background_color, text="密码").grid(row=1, column=0, pady=10, padx=5)
            Label(frame_signin_form, bg=self.background_color, text="确认密码").grid(row=2, column=0, pady=10, padx=5)
            Label(frame_signin_form, bg=self.background_color, text="姓名").grid(row=3, column=0, pady=10, padx=5)
            Label(frame_signin_form, bg=self.background_color, text="身份码").grid(row=4, column=0, pady=10, padx=5)
            entry_un_new = Entry(frame_signin_form, font="TkDefaultFont")
            entry_un_new.grid(row=0, column=1, columnspan=3, pady=10)
            entry_pw_new = Entry(frame_signin_form, font="TkDefaultFont")
            entry_pw_new.grid(row=1, column=1, columnspan=3)
            entry_pw_again = Entry(frame_signin_form, font="TkDefaultFont")
            entry_pw_again.grid(row=2, column=1, columnspan=3)
            entry_name = Entry(frame_signin_form, font="TkDefaultFont")
            entry_name.grid(row=3, column=1, columnspan=3)
            entry_code = Entry(frame_signin_form, font="TkDefaultFont")
            entry_code.grid(row=4, column=1, columnspan=3)
            Button(frame_signin_form, text="提交", command=submit).grid(row=5, column=1, columnspan=2, pady=10)
            Button(frame_signin_form, text="返回", command=back).grid(row=6, column=1, columnspan=2)
            Label(frame_signin,
                  text="说明: 除旅客用户外, 其他用户注册必须填写姓名和身份码",
                  bg=self.background_color).pack(pady=20, side="bottom")

        def forgot():
            # 忘记密码
            messagebox.showinfo("提示", "请联系超级管理员修改密码")

        self.frame_login.pack(expand=1)
        Label(self.frame_login, bg=self.background_color, text=f"欢迎使用{self.systemName}系统", font=("黑体", 20)) \
            .pack(pady=20)
        frame = Frame(self.frame_login, bg=self.background_color)
        frame.pack()
        Label(frame, bg=self.background_color, text="账号").grid(row=0, column=0, pady=10)
        Label(frame, bg=self.background_color, text="密码").grid(row=1, column=0)
        entry_un = Entry(frame, font="TkDefaultFont")
        entry_un.grid(row=0, column=1, columnspan=3, pady=10)
        entry_pw = Entry(frame, font="TkDefaultFont")
        entry_pw.grid(row=1, column=1, columnspan=3)
        Button(frame, text="登录", command=login).grid(row=2, column=1, pady=10)
        Button(frame, text="注册", command=signin).grid(row=2, column=2)
        Button(frame, text="忘记密码", command=forgot).grid(row=3, column=1, columnspan=2)

    # 旅客窗口
    def traveller(self):
        def table():
            status = {401: "取消", 402: "管制", 403: "安全", 404: "事故",
                      301: "净空", 302: "延迟", 303: "天气恶劣", 304: "临时检查",
                      201: "等待", 202: "检票", 203: "登机", 204: "滑出"}
            datas = self.onSelect('Fno, Fli_range, Fli_date, Fli_state', self.fis, None, None)
            cols = self.fis_col[:4]
            tree = Treeview(frame)
            tree["show"] = "headings"
            tree["columns"] = cols
            tree.column(cols[0], width=100)
            tree.column(cols[1], width=100)
            tree.column(cols[2], width=100)
            tree.column(cols[3], width=100)
            tree.heading(cols[0], text="航班号")
            tree.heading(cols[1], text="起降地")
            tree.heading(cols[2], text="预计起降时间")
            tree.heading(cols[3], text="航班状态")
            for i, row in enumerate(datas):
                tree.insert("", i + 1, text=str(i), values=row[:3] + (status.get(int(row[3]), "状态错误"),))
            return tree

        def back():
            self.frame_welcome.pack_forget()
            self.frame_login.pack(expand=1)
            window.destroy()

        window = Tk()
        window.title("航班信息一览")
        window.resizable(False, False)
        window.attributes("-topmost", True)

        frame = Frame(window)
        frame.grid(row=0, column=0, columnspan=2)
        self.tree = table()
        self.tree.pack()

        Button(window, text="退出登录", command=back).grid(row=1, column=1)

        window.protocol("WM_DELETE_WINDOW", back)
        window.mainloop()

    # 地勤窗口
    def ground(self):
        def submit():
            def check():
                tg = entry_sm_tg.get()
                cn = entry_sm_cn.get()
                jn = entry_sm_jn.get()
                no = str(calendar.timegm(time.gmtime())) + "" + str(jn)
                if tg is None or cn is None:
                    messagebox.showerror("错误", "提交内容不能为空")
                else:
                    datas = self.onSelect('*', self.gi, (no, None, None, None), None)
                    if len(datas) == 0:
                        self.onInsert(self.gi, [(no, tg, cn, jn)])
                        win_sm.destroy()
                    else:
                        messagebox.showerror("错误", f"操作失败\n{datas}")

            win_sm = Tk()
            win_sm.title("提交信息")
            window.resizable(False, False)
            Label(win_sm, text="跑道编号").grid(row=0, column=0)
            Label(win_sm, text="跑道情况").grid(row=1, column=0)
            Label(win_sm, text="地勤工号").grid(row=2, column=0)
            entry_sm_tg = Entry(win_sm)
            entry_sm_tg.grid(row=0, column=1, columnspan=2, padx=5, pady=10)
            entry_sm_cn = Entry(win_sm)
            entry_sm_cn.grid(row=1, column=1, columnspan=2, padx=5, pady=10)
            entry_sm_jn = Entry(win_sm)
            entry_sm_jn.insert(END, self.username)
            entry_sm_jn.config(state='readonly')
            entry_sm_jn.grid(row=2, column=1, columnspan=2, padx=5, pady=10)
            Button(win_sm, text="确认", command=check).grid(row=3, column=1)
            win_sm.mainloop()

        def gi_his():
            win_gi = Tk()
            win_gi.title("跑道信息")
            window.resizable(False, False)

            datas = self.onSelect('G_number, Gno, G_info', self.gi, None, None)
            cols = self.gi_col[:3]
            tree_gi = Treeview(win_gi)
            tree_gi["show"] = "headings"
            tree_gi["columns"] = cols
            for i in range(0, 3):
                tree_gi.column(cols[i], width=150)
            tree_gi.heading(cols[0], text="情况编号")
            tree_gi.heading(cols[1], text="跑道号")
            tree_gi.heading(cols[2], text="跑道情况")
            for i, row in enumerate(datas):
                tree_gi.insert("", i + 1, text=str(i), values=row)
            tree_gi.pack()

            win_gi.mainloop()

        def back():
            self.frame_welcome.pack_forget()
            self.frame_login.pack(expand=1)
            window.destroy()

        window = Tk()
        window.title("跑道信息汇报")
        window.resizable(False, False)
        window.attributes("-topmost", True)

        frame_btn = LabelFrame(window, text="操作台")
        frame_btn.pack()
        Button(frame_btn, text="提交跑道信息", command=submit).grid(row=0, column=0, padx=5, pady=10)
        Button(frame_btn, text="查看跑道信息", command=gi_his).grid(row=0, column=1, padx=5, pady=10)

        tree_fis = self.table_fis(window)
        tree_fis.pack()

        Button(window, text="退出登录", command=back).pack()

        window.protocol("WM_DELETE_WINDOW", back)
        window.mainloop()

    # 塔台窗口
    def tower(self):
        def submit():
            def check():
                jn = self.username
                cn = entry_sm_cn.get()
                tg = entry_sm_tg.get()
                lc = entry_sm_lc.get()
                no = str(calendar.timegm(time.gmtime())) + "" + str(jn)
                if cn == '' or tg == '' or lc == '':
                    messagebox.showerror("错误", "提交内容不能为空")
                else:
                    no_gi = self.onSelect('MAX(G_number)', self.gi, (None, lc, None, None), None)[0][0]
                    tg_sel = self.onSelect('*', self.fis, (tg, None, None, None, None), None)

                    if no_gi is None or tg_sel == ():
                        messagebox.showerror("错误", "信息有误, 请重试")
                    else:
                        if messagebox.askokcancel("提示", f"即将添加以下数据:\n{(jn, cn, tg, lc)}"):
                            self.onInsert(self.ctc, [(no, cn, jn)])
                            self.onInsert(self.fc, [(no, tg, no_gi)])
                            messagebox.showinfo("提示", "修改成功")

            win_sm = Tk()
            win_sm.title("提交调度")
            window.resizable(False, False)

            Label(win_sm, text="塔台工号").grid(row=0, column=0)
            Label(win_sm, text="指令内容").grid(row=1, column=0)
            Label(win_sm, text="指令目标").grid(row=2, column=0)
            Label(win_sm, text="目标位置").grid(row=3, column=0)
            entry_sm_jn = Entry(win_sm)
            entry_sm_jn.insert(END, self.username)
            entry_sm_jn.config(state='readonly')
            entry_sm_jn.grid(row=0, column=1, columnspan=2, padx=5, pady=10)
            entry_sm_cn = Entry(win_sm)
            entry_sm_cn.grid(row=1, column=1, columnspan=2, padx=5, pady=10)
            entry_sm_tg = Entry(win_sm)
            entry_sm_tg.grid(row=2, column=1, columnspan=2, padx=5, pady=10)
            entry_sm_lc = Entry(win_sm)
            entry_sm_lc.grid(row=3, column=1, columnspan=2, padx=5, pady=10)
            Button(win_sm, text="确认", command=check).grid(row=4, column=1)

            win_sm.mainloop()

        def tc_his():
            win_tc = Tk()
            win_tc.title("调度历史")
            window.resizable(False, False)
            tree_tc = self.table_ctc(win_tc)
            tree_tc.pack()
            win_tc.mainloop()

        def gi_his():
            win_gi = Tk()
            win_gi.title("跑道信息")
            window.resizable(False, False)
            tree_gi = self.table_gi(win_gi)
            tree_gi.pack()
            win_gi.mainloop()

        def back():
            self.frame_welcome.pack_forget()
            self.frame_login.pack(expand=1)
            window.destroy()

        window = Tk()
        window.title("塔台调度平台")
        window.resizable(False, False)
        window.attributes("-topmost", True)

        frame_btn = LabelFrame(window, text="操作台")
        frame_btn.pack()
        Button(frame_btn, text="提交调度指令", command=submit).grid(row=0, column=0, padx=5, pady=10)
        Button(frame_btn, text="查看调度历史", command=tc_his).grid(row=0, column=1, padx=5, pady=10)
        Button(frame_btn, text="查看跑道信息", command=gi_his).grid(row=0, column=2, padx=5, pady=10)

        tree = self.table_fis(window)
        tree.pack()

        Button(window, text="退出登录", command=back).pack()

        window.protocol("WM_DELETE_WINDOW", back)
        window.mainloop()

    # 管理员窗口
    def admin(self):
        def gi():
            win_gi = Tk()
            win_gi.title("跑道信息")
            window.resizable(False, False)
            tree_gi = self.table_gi(win_gi)
            tree_gi.pack()
            win_gi.mainloop()

        def ctc():
            win_tc = Tk()
            win_tc.title("调度历史")
            window.resizable(False, False)
            tree_tc = self.table_ctc(win_tc)
            tree_tc.pack()
            win_tc.mainloop()

        def fi():
            def submit():
                fli = entry.get()
                if fli == '':
                    messagebox.showerror("错误", "提交内容不能为空")
                else:
                    data = self.onSelect('*', self.fis, (fli, None, None, None, None), None)
                    if len(data) == 0:
                        messagebox.showerror("错误", f"航班{fli}不存在")
                    elif len(data) > 1:
                        messagebox.showerror("错误", "too many")
                    else:
                        data_fis = data[0]
                        data_gi = self.onSelect('*', self.gi, None,
                                                f''' AND {self.gi_col[0]}=\'{self.onSelect(f'MAX({self.fc_col[2]})', self.fc, (None, fli, None), None)[0][0]}\';''')[
                            0]
                        data_ctc = self.onSelect('*', self.ctc, None,
                                                 f''' AND {self.ctc_col[0]}=\'{self.onSelect(f'MAX({self.fc_col[0]})', self.fc, (None, fli, None), None)[0][0]}\';''')[
                            0]
                        print(data_fis)
                        print(data_gi)
                        print(data_ctc)
                        messagebox.showinfo("结果",
                                            f'''航班号: {data_fis[0]}, 航班区间: {data_fis[1]}, 起降时间: {data_fis[2]}, 
航班状态码: {data_fis[3]}, 航班机型: {data_fis[4]}.
跑道号: {data_gi[1]}, 跑道情况: {data_gi[2]}, 汇报人: {data_gi[3]}.
塔台指令: {data_ctc[1]}, 调度员: {data_ctc[2]}.''')
                        win_fi.destroy()

            win_fi = Tk()
            win_fi.title("航班相关信息")
            win_fi.resizable(False, False)
            win_fi.attributes("-topmost", True)
            Label(win_fi, text="输入需要查询的航班").grid(row=0, column=0)
            entry = Entry(win_fi)
            entry.grid(row=0, column=1, columnspan=2)
            Button(win_fi, text="查询", command=submit).grid(row=1, column=1)
            win_fi.mainloop()

        def fis_sel():
            control(1)

        def fis_ins():
            control(2)

        def fis_del():
            control(3)

        def fis_upd():
            control(4)

        def control(value):
            def submit():
                data_new = (entry_no.get(), entry_rg.get(), entry_dt.get(), entry_st.get(), entry_tp.get())
                data_sel = self.onSelect('*', self.fis, data_new, None)
                if 0 < value < 4:
                    if len(data_sel) == 0:
                        if value == 1:
                            messagebox.showinfo("提示", "无查询结果")
                        elif value == 2:
                            if messagebox.askokcancel("提示", f"即将插入以下数据:\n{data_new}"):
                                self.onInsert(self.fis, [data_new])
                        elif value == 3:
                            messagebox.showerror("错误", "数据不存在, 删除失败")
                    else:
                        res = ""
                        for data in data_sel:
                            res += "\n" + str(data).replace("'", "")
                        if value == 1:
                            messagebox.showinfo("提示", f"查得以下数据:{res}")
                        elif value == 2:
                            messagebox.showerror("错误", f"相关数据已存在:{res}")
                        elif value == 3:
                            if messagebox.askokcancel("提示", f"即将删除以下数据:{res}"):
                                for data in data_sel:
                                    self.onDelete(self.fis, data[0])
                if value == 4:
                    data_sel = self.onSelect('*', self.fis,
                                             (entry_no.get(), None, None, None, None), None)
                    if len(data_sel) == 0:
                        messagebox.showerror("错误", "数据不存在, 修改失败")
                    else:
                        for data in data_sel:
                            data_upd = []
                            for i, j in zip(data_new, data):
                                if i == '':
                                    data_upd.append(j)
                                else:
                                    data_upd.append(i)
                            self.onUpdate(self.fis, tuple(data_upd))
                win_ctrl.destroy()

            status = {1: "查找", 2: "插入", 3: "删除", 4: "修改"}
            win_ctrl = Tk()
            win_ctrl.title(f"{status[value]}操作")
            win_ctrl.resizable(False, False)

            label = Label(win_ctrl, text="输入新数据")
            if value == 4:
                label.grid(row=0, column=1, pady=10)
            Label(win_ctrl, text="航班号").grid(row=1, column=0, padx=5, pady=10)
            Label(win_ctrl, text="飞行区间").grid(row=2, column=0, padx=5, pady=10)
            Label(win_ctrl, text="起降时间").grid(row=3, column=0, padx=5, pady=10)
            Label(win_ctrl, text="航班状态码").grid(row=4, column=0, padx=5, pady=10)
            Label(win_ctrl, text="机型").grid(row=5, column=0, padx=5, pady=10)
            entry_no = Entry(win_ctrl)
            entry_no.grid(row=1, column=1, columnspan=2)
            entry_rg = Entry(win_ctrl)
            entry_rg.grid(row=2, column=1, columnspan=2)
            entry_dt = Entry(win_ctrl)
            entry_dt.grid(row=3, column=1, columnspan=2)
            entry_st = Entry(win_ctrl)
            entry_st.grid(row=4, column=1, columnspan=2)
            entry_tp = Entry(win_ctrl)
            entry_tp.grid(row=5, column=1, columnspan=2)
            Button(win_ctrl, text="提交", command=submit).grid(row=6, column=1)

            win_ctrl.mainloop()

        def fresh():
            self.tree.pack_forget()
            self.tree = self.table_fis(frame_tree)
            self.tree.pack()

        def back():
            self.frame_welcome.pack_forget()
            self.frame_login.pack(expand=1)
            window.destroy()

        window = Tk()
        window.title("管理员控制台")
        window.resizable(False, False)
        window.attributes("-topmost", True)

        frame_btn1 = Frame(window)
        frame_btn1.pack()
        Button(frame_btn1, text="查看跑道情况", command=gi).grid(row=0, column=0, padx=5, pady=10)
        Button(frame_btn1, text="查看塔台调度", command=ctc).grid(row=0, column=1, padx=5)
        Button(frame_btn1, text="查询航班信息", command=fi).grid(row=0, column=2, padx=5)

        frame_btn2 = LabelFrame(window, text="航班信息表操作")
        frame_btn2.pack()
        Button(frame_btn2, text="查找", command=fis_sel).grid(row=0, column=0, padx=5, pady=5)
        Button(frame_btn2, text="添加", command=fis_ins).grid(row=0, column=1, padx=5, pady=5)
        Button(frame_btn2, text="删除", command=fis_del).grid(row=0, column=2, padx=5, pady=5)
        Button(frame_btn2, text="修改", command=fis_upd).grid(row=0, column=3, padx=5, pady=5)

        frame_tree = Frame(window)
        frame_tree.pack()
        self.tree = self.table_fis(frame_tree)
        self.tree.pack()

        frame_btn3 = Frame(window)
        frame_btn3.pack()
        Button(frame_btn3, text="页面刷新", command=fresh).grid(row=0, column=0, padx=10, pady=10)
        Button(frame_btn3, text="退出登录", command=back).grid(row=0, column=1)

        window.protocol("WM_DELETE_WINDOW", back)
        window.mainloop()

    # 超级管理员窗口
    def root(self):
        def tb_us():
            def pwdChange():
                def submit():
                    un = entry_un.get()
                    pw = entry_pw.get()
                    if un == '' or pw == '':
                        messagebox.showerror("错误", "提交内容不能为空")
                    else:
                        data = self.onSelect('*', self.us, (un, None, None, None), None)
                        if len(data) == 0 or len(data) > 1:
                            messagebox.showerror("错误", "用户信息错误, 修改失败")
                        else:
                            try:
                                self.onUpdate(self.us, (un, (base64.b64encode(pw.encode('utf-8'))).decode('utf-8'),
                                                        data[0][2], data[0][3]))
                                messagebox.showinfo("提示", "操作成功")
                                win_pc.destroy()
                            except Exception as e:
                                messagebox.showerror("错误", f"出现错误:\n{e}\n操作失败")

                win_pc = Tk()
                win_pc.title("修改密码")
                win_pc.attributes("-topmost", True)
                win_pc.resizable(False, False)
                Label(win_pc, text="账户").grid(row=0, column=0, padx=5, pady=10)
                Label(win_pc, text="新密码").grid(row=1, column=0, padx=5, pady=10)
                entry_un = Entry(win_pc)
                entry_un.grid(row=0, column=1, columnspan=2)
                entry_pw = Entry(win_pc)
                entry_pw.grid(row=1, column=1, columnspan=2)
                Button(win_pc, text="确认", command=submit).grid(row=2, column=1)
                win_pc.mainloop()

            def usrDelete():
                def submit():
                    un = entry.get()
                    if un == "root":
                        messagebox.showerror("错误", "无法删除 root 用户")
                    elif un == '':
                        messagebox.showerror("错误", "输入为空值")
                    else:
                        data = self.onSelect('*', self.us, (un, None, None, None), None)
                        print(data)
                        if len(data) == 0 or len(data) > 1:
                            messagebox.showerror("错误", "用户信息错误, 操作失败")
                        else:
                            try:
                                self.onDelete(self.us, un)
                                messagebox.showinfo("提示", "操作成功")
                                win_ud.destroy()
                            except Exception as e:
                                messagebox.showerror("错误", f"出现错误:\n{e}\n操作失败")

                win_ud = Tk()
                win_ud.title("用户删除")
                win_ud.attributes("-topmost", True)
                win_ud.resizable(False, False)
                Label(win_ud, text="账号").grid(row=0, column=0, padx=5, pady=10)
                entry = Entry(win_ud)
                entry.grid(row=0, column=1, columnspan=2)
                Button(win_ud, text="删除该用户", command=submit).grid(row=1, column=1)
                win_ud.mainloop()

            def usrCreate():
                def submit():
                    un_new = entry_un.get()
                    pw_new = entry_pw.get()
                    nm_new = entry_nm.get()
                    id_new = entry_id.get()
                    if un_new == '' or pw_new == '' or id_new == '':
                        messagebox.showerror("错误", "提交信息不能为空")
                    else:
                        data = self.onSelect('*', self.us, (un_new, None, None, None), None)
                        if len(data) != 0:
                            messagebox.showerror("错误", f"用户{un_new}已存在")
                        else:
                            try:
                                id_num = int(id_new)
                                if 0 < id_num < 6:
                                    if messagebox.askokcancel("提示", f"即将插入新用户：{un_new}, 密码为{pw_new}, " +
                                                                    f"姓名为{nm_new if not '' else 'null'}, 身份为{id_new}"):
                                        self.onInsert(self.us, [(un_new,
                                                                 (base64.b64encode(pw_new.encode('utf-8')))
                                                                 .decode('utf-8'), nm_new, id_new)])
                                        win_uc.destroy()
                                    else:
                                        messagebox.showinfo("提示", "用户创建取消")
                                else:
                                    messagebox.showerror("错误", "用户身份信息错误")
                            except Exception as e:
                                messagebox.showerror("错误", f"出现错误:\n{e}\n操作失败")

                win_uc = Tk()
                win_uc.title("新增用户")
                win_uc.attributes("-topmost", True)
                win_uc.resizable(False, False)

                Label(win_uc, text="账号").grid(row=0, column=0, padx=5, pady=10)
                Label(win_uc, text="密码").grid(row=1, column=0, padx=5, pady=10)
                Label(win_uc, text="姓名").grid(row=2, column=0, padx=5, pady=10)
                Label(win_uc, text="身份").grid(row=3, column=0, padx=5, pady=10)
                entry_un = Entry(win_uc)
                entry_un.grid(row=0, column=1, columnspan=2)
                entry_pw = Entry(win_uc)
                entry_pw.grid(row=1, column=1, columnspan=2)
                entry_nm = Entry(win_uc)
                entry_nm.grid(row=2, column=1, columnspan=2)
                entry_id = Entry(win_uc)
                entry_id.grid(row=3, column=1, columnspan=2)
                Button(win_uc, text="提交", command=submit).grid(row=4, column=1)

                win_uc.mainloop()

            def table():
                status = {1: "旅客", 2: "地勤", 3: "塔台", 4: "管理", 5: "超管"}
                datas = self.onSelect('Uno, Username, Identy', self.us, None, None)
                cols = (self.us_col[0],) + self.us_col[2:]
                tree = Treeview(frame_tree)
                tree["show"] = "headings"
                tree["columns"] = cols
                for i in range(0, 3):
                    tree.column(cols[i], width=100)
                tree.heading(cols[0], text="账号")
                tree.heading(cols[1], text="姓名")
                tree.heading(cols[2], text="身份")
                for i, row in enumerate(datas):
                    tree.insert("", i + 1, text=str(i), values=row[:2] + (status.get(int(row[2]), "身份错误"),))
                return tree

            def dataFresh():
                self.tree.pack_forget()
                self.tree = table()
                self.tree.pack()

            win_us = Tk()
            win_us.title("用户信息")
            win_us.attributes("-topmost", True)
            win_us.resizable(False, False)

            frame_tree = Frame(win_us)
            frame_tree.pack()
            self.tree = table()
            self.tree.pack()

            frame = Frame(win_us)
            frame.pack()
            Button(frame, text="修改密码", command=pwdChange).grid(row=0, column=0, padx=5)
            Button(frame, text="删除用户", command=usrDelete).grid(row=0, column=1, padx=5)
            Button(frame, text="增加用户", command=usrCreate).grid(row=0, column=2, padx=5)
            Button(frame, text="刷新数据", command=dataFresh).grid(row=0, column=3, padx=5)

            win_us.mainloop()

        def tb_fis():
            def submit():
                cmd = cbb.get() + self.fis + " " + entry.get()
                if cmd == '':
                    messagebox.showerror("错误", "命令不能为空")
                else:
                    try:
                        self.cursor.execute(cmd)
                        result = self.cursor.fetchall()
                        if result == ():
                            messagebox.showinfo("提示", "操作成功")
                            self.tree.pack_forget()
                            self.tree = self.table_fis(frame)
                            self.tree.pack()
                        else:
                            messagebox.showinfo("提示", f"操作结果:\n{result}")
                    except Exception as e:
                        messagebox.showerror("错误", f"出现错误:\n{e}\n操作失败")

            win_fis = Tk()
            win_fis.title("航班信息")
            win_fis.attributes("-topmost", True)
            win_fis.resizable(False, False)

            frame = Frame(win_fis)
            frame.grid(row=0, column=0, columnspan=4, pady=10)
            self.tree = self.table_fis(frame)
            self.tree.pack()

            var = StringVar()
            cbb = Combobox(win_fis, textvariable=var, values=(
                'SELECT * FROM ', 'INSERT INTO ', 'DELETE FROM ', 'UPDATE '))
            cbb.current(0)
            cbb.grid(row=1, column=0, padx=5, pady=10)
            Label(win_fis, text=self.fis).grid(row=1, column=1, padx=5)
            entry = Entry(win_fis)
            entry.grid(row=1, column=2, padx=5)
            Button(win_fis, text="执行", command=submit).grid(row=1, column=3, padx=5)

            win_fis.mainloop()

        def tb_gi():
            def submit():
                cmd = cbb.get() + self.gi + " " + entry.get()
                if cmd == '':
                    messagebox.showerror("错误", "命令不能为空")
                else:
                    try:
                        self.cursor.execute(cmd)
                        result = self.cursor.fetchall()
                        if result == ():
                            messagebox.showinfo("提示", "操作成功")
                            self.tree.pack_forget()
                            self.tree = self.table_gi(frame)
                            self.tree.pack()
                        else:
                            messagebox.showinfo("提示", f"操作结果:\n{result}")
                    except Exception as e:
                        messagebox.showerror("错误", f"出现错误:\n{e}\n操作失败")

            win_gi = Tk()
            win_gi.title("跑道情况")
            win_gi.attributes("-topmost", True)
            win_gi.resizable(False, False)

            frame = Frame(win_gi)
            frame.grid(row=0, column=0, columnspan=4, pady=10)
            self.tree = self.table_gi(frame)
            self.tree.pack()

            var = StringVar()
            cbb = Combobox(win_gi, textvariable=var, values=(
                'SELECT * FROM ', 'INSERT INTO ', 'DELETE FROM ', 'UPDATE '))
            cbb.current(0)
            cbb.grid(row=1, column=0, padx=5, pady=10)
            Label(win_gi, text=self.gi).grid(row=1, column=1, padx=5)
            entry = Entry(win_gi)
            entry.grid(row=1, column=2, padx=5)
            Button(win_gi, text="执行", command=submit).grid(row=1, column=3, padx=5)

            win_gi.mainloop()

        def tb_ctc():
            def submit():
                cmd = cbb.get() + self.ctc + " " + entry.get()
                if cmd == '':
                    messagebox.showerror("错误", "命令不能为空")
                else:
                    try:
                        self.cursor.execute(cmd)
                        result = self.cursor.fetchall()
                        if result == ():
                            messagebox.showinfo("提示", "操作成功")
                            self.tree.pack_forget()
                            self.tree = self.table_ctc(frame)
                            self.tree.pack()
                        else:
                            messagebox.showinfo("提示", f"操作结果:\n{result}")
                    except Exception as e:
                        messagebox.showerror("错误", f"出现错误:\n{e}\n操作失败")

            win_ctc = Tk()
            win_ctc.title("塔台调度")
            win_ctc.attributes("-topmost", True)
            win_ctc.resizable(False, False)

            frame = Frame(win_ctc)
            frame.grid(row=0, column=0, columnspan=4, pady=10)
            self.tree = self.table_ctc(frame)
            self.tree.pack()

            var = StringVar()
            cbb = Combobox(win_ctc, textvariable=var, values=(
                'SELECT * FROM ', 'INSERT INTO ', 'DELETE FROM ', 'UPDATE '))
            cbb.current(0)
            cbb.grid(row=1, column=0, padx=5, pady=10)
            Label(win_ctc, text=self.ctc).grid(row=1, column=1, padx=5)
            entry = Entry(win_ctc)
            entry.grid(row=1, column=2, padx=5)
            Button(win_ctc, text="执行", command=submit).grid(row=1, column=3, padx=5)

            win_ctc.mainloop()

        def showAll():
            def submit():
                fli = entry.get()
                if fli == '':
                    messagebox.showerror("错误", "提交内容不能为空")
                else:
                    data = self.onSelect('*', self.fis, (fli, None, None, None, None), None)
                    if len(data) == 0:
                        messagebox.showerror("错误", f"航班{fli}不存在")
                    elif len(data) > 1:
                        messagebox.showerror("错误", "too many")
                    else:
                        data_fis = data[0]
                        data_gi = self.onSelect('*', self.gi, None,
                                                f''' AND {self.gi_col[0]}=\'{self.onSelect(f'MAX({self.fc_col[2]})', self.fc, (None, fli, None), None)[0][0]}\';''')[
                            0]
                        data_ctc = self.onSelect('*', self.ctc, None,
                                                 f''' AND {self.ctc_col[0]}=\'{self.onSelect(f'MAX({self.fc_col[0]})', self.fc, (None, fli, None), None)[0][0]}\';''')[
                            0]
                        print(data_fis)
                        print(data_gi)
                        print(data_ctc)
                        messagebox.showinfo("结果",
                                            f'''航班号: {data_fis[0]}, 航班区间: {data_fis[1]}, 起降时间: {data_fis[2]}, 
航班状态码: {data_fis[3]}, 航班机型: {data_fis[4]}.
跑道号: {data_gi[1]}, 跑道情况: {data_gi[2]}, 汇报人: {data_gi[3]}.
塔台指令: {data_ctc[1]}, 调度员: {data_ctc[2]}.''')
                        win_sa.destroy()

            def history():
                win_sa_history = Tk()
                win_sa_history.title("历史记录")
                win_sa_history.resizable(False, False)
                win_sa_history.attributes("-topmost", True)

                datas = self.onSelect('*', self.fc, None, None)
                cols = self.fc_col
                tree = Treeview(win_sa_history)
                tree["show"] = "headings"
                tree["columns"] = cols
                for i in range(0, 3):
                    tree.column(cols[i], width=150)
                tree.heading(cols[0], text="调度编号")
                tree.heading(cols[1], text="航班号")
                tree.heading(cols[2], text="情况编号")
                for i, row in enumerate(datas):
                    tree.insert("", i + 1, text=str(i), values=row)
                tree.pack()

                win_sa_history.mainloop()

            win_sa = Tk()
            win_sa.title("航班相关信息")
            win_sa.attributes("-topmost", True)
            win_sa.resizable(False, False)

            Label(win_sa, text="航班号").grid(row=0, column=0, pady=10)
            entry = Entry(win_sa)
            entry.grid(row=0, column=1, columnspan=2)
            Button(win_sa, text="提交查询目标", command=submit).grid(row=1, column=0, padx=10)
            Button(win_sa, text="查看全部历史", command=history).grid(row=1, column=1)

            win_sa.mainloop()

        def back():
            self.frame_welcome.pack_forget()
            self.frame_login.pack(expand=1)
            window.destroy()

        window = Tk()
        window.title("超级管理员")
        window.resizable (False, False)
        window.attributes("-topmost", True)

        frame_btn = Frame(window)
        frame_btn.pack()
        Button(frame_btn, text="用户信息表", command=tb_us).grid(row=0, column=0, padx=5, pady=10)
        Button(frame_btn, text="航班信息表", command=tb_fis).grid(row=0, column=1, padx=5, pady=10)
        Button(frame_btn, text="跑道信息表", command=tb_gi).grid(row=1, column=0, padx=5, pady=10)
        Button(frame_btn, text="塔台信息表", command=tb_ctc).grid(row=1, column=1, padx=5, )

        Button(window, text="查看指定航班相关信息", command=showAll).pack(pady=10)

        Button(window, text="退出登录", command=back).pack()

        window.protocol("WM_DELETE_WINDOW", back)
        window.mainloop()

    # 主窗口关闭函数
    def onClose(self):
        if messagebox.askokcancel("退出", "是否确定退出"):
            try:
                print("close")
                self.onDrop()
                self.cursor.close()
                self.db.close()
            except Exception as e:
                print(e)
            finally:
                self.window.destroy()

    # endregion

    # region 数据库操作
    # 连接/创建数据库
    def connect2database(self):
        try:
            self.db = pymysql.connect(
                host='localhost',
                user=self.dbUsr,
                password=self.dbPwd,
                database=self.database,
                charset='utf8'
            )
            self.cursor = self.db.cursor()
            try:
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS User_Set(
                Uno CHAR(20),
                Password CHAR(20),
                Username CHAR(20),
                Identy CHAR(10),
                PRIMARY KEY(Uno)
                );''')  # 用户表
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS Flight_info_show(
                Fno CHAR(20),
                Fli_range CHAR(20),
                Fli_date CHAR(20),
                Fli_state CHAR(10),
                Fli_type CHAR(10),
                PRIMARY KEY(Fno)
                );''')  # 航班信息表
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS Ground_Info(
                G_number CHAR(20),
                Gno CHAR(20),
                G_info CHAR(10),
                G_worker CHAR(10),
                PRIMARY KEY (G_number)
                );''')  # 跑道情况表
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS CT_Control(
                Cno CHAR(20),
                Cname CHAR(10),
                C_worker CHAR(10),
                PRIMARY KEY(Cno)
                );''')  # 塔台调度表
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS Fli_Control( 
                Cno CHAR(20),
                Fno CHAR(20),
                G_number CHAR(20),
                FOREIGN KEY (Cno) REFERENCES CT_Control(Cno) ON DELETE CASCADE,
                FOREIGN KEY(Fno) REFERENCES Flight_info_show(Fno) ON DELETE CASCADE,
                FOREIGN KEY(G_number) REFERENCES Ground_Info(G_number) ON DELETE CASCADE
                );''')  # 航班调度表

                self.onInsert(self.us, [("user", base64.b64encode(b"user"), '', "1"),
                                        ("2101", base64.b64encode(b"2101"), '张三', "2"),
                                        ("2201", base64.b64encode(b"2201"), '李四', "3"),
                                        ("admin", base64.b64encode(b"admin"), '王五', "4"),
                                        ("root", base64.b64encode(b"root"), "root", "5")])
                number_flight_a = 'BA1326'
                number_flight_b = 'MU1322'
                self.onInsert(self.fis, [(number_flight_a, '北京-上海', '14:00-17:00', '404', '747'),
                                         (number_flight_b, '北京-上海', '16:00-19:00', '201', '747')])
                number_gc = str(calendar.timegm(time.gmtime())) + str(2101)
                self.onInsert(self.gi, [(number_gc, 'A1', '净空', '2101')])
                number_tc = str(calendar.timegm(time.gmtime())) + str(2201)
                self.onInsert(self.ctc, [(number_tc, '允许起飞', '2201')])
                self.onInsert(self.fc, [(number_tc, number_flight_a, number_gc),
                                        (number_tc, number_flight_b, number_gc)])
            except Exception as e:
                print(e)
            self.window_user()
        except Exception as e:
            print(e)

    # 数据库查找操作
    def onSelect(self, target, table, datas, condition):
        try:
            columns = self.columns[table]
            if target is None:
                target = '*'
            sql = f"SELECT {target} FROM " + table + " WHERE 1=1"
            if condition is None:
                if datas is not None:
                    for i in range(len(columns)):
                        if datas[i] is not None and datas[i] != '':
                            sql += f" AND {columns[i]}=\'{datas[i]}\'"
            else:
                sql += condition
            try:
                self.cursor.execute(sql)
                return self.cursor.fetchall()
            except Exception as e:
                print(e)
                self.db.rollback()
                return None
        except Exception as e:
            print(e)
            return None

    # 数据库插入操作
    def onInsert(self, table, datas):
        try:
            columns = self.columns[table]
            sql = "INSERT INTO " + table + " " + str(columns).replace("'", "") + " VALUES "
            string = ""
            for i in range(len(columns)):
                string += "%s"
                if i != len(columns) - 1:
                    string += ","
            sql += "(" + string + ");"
            self.cursor.executemany(sql, datas)
            try:
                self.db.commit()
                print("插入操作成功")
            except Exception as e:
                print(e)
                self.db.rollback()
        except Exception as e:
            print(e)

    # 数据库删除操作
    def onDelete(self, table, primary_key):
        try:
            columns = self.columns[table]
            sql = "DELETE FROM " + table + " WHERE " + columns[0] + " =\'%s\';"
            self.cursor.execute(sql % primary_key)
            try:
                self.db.commit()
                print("删除操作成功")
            except Exception as e:
                print(e)
                self.db.rollback()
        except Exception as e:
            print(e)

    # 数据库更新操作
    def onUpdate(self, table, datas):
        if table == self.fc:
            messagebox.showerror("错误", "无法进行更新操作")
            return
        try:
            columns = self.columns[table]
            datas = datas[1:] + (datas[0],)
            sql = "UPDATE " + table + " SET "
            for i in range(len(columns)):
                if i != 0:
                    sql += columns[i] + "=\'%s\'"
                    if i != len(columns) - 1:
                        sql += ","
            sql += " WHERE " + columns[0] + "=\'%s\';"
            self.cursor.execute(sql % datas)
            try:
                self.db.commit()
                print("更新操作成功")
            except Exception as e:
                print(e)
                self.db.rollback()
        except Exception as e:
            print(e)

    # 数据库删表操作
    def onDrop(self):
        tables = [self.us, self.fc, self.fis, self.gi, self.ctc]
        for table in tables:
            self.cursor.execute('DROP TABLE IF EXISTS %s' % table)
        self.cursor.execute('show tables')
        print(self.cursor.fetchall())
    # endregion


if __name__ == '__main__':
    app = App()
