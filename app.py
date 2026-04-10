"""Unsplash 图片搜索工具 v2 - 支持中文搜索"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
import os
import threading
from datetime import datetime
from config import ACCESS_KEY, SEARCH_URL, PER_PAGE

search_results = []
current_page = 1
total_pages = 1
is_searching = False


def translate_to_english(text):
    """将中文翻译成英文"""
    if not text or not text.strip():
        return ""
    try:
        text.encode("ascii")
        return text.strip()
    except UnicodeEncodeError:
        pass
    url = "https://api.mymemory.translated.net/get"
    params = {"q": text, "langpair": "zh-CN|en"}
    try:
        resp = requests.get(url, params=params, timeout=10)
        data = resp.json()
        if data.get("responseStatus") == 200:
            return data["responseData"]["translatedText"]
    except Exception:
        pass
    return text.strip()


def search_photos(query, page=1):
    headers = {"Authorization": f"Client-ID {ACCESS_KEY}"}
    params = {"query": query, "page": page, "per_page": PER_PAGE}
    try:
        resp = requests.get(SEARCH_URL, headers=headers, params=params, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {"error": str(e)}


def download_image(url, filepath):
    try:
        resp = requests.get(url, timeout=30, stream=True)
        resp.raise_for_status()
        with open(filepath, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception:
        return False


def get_default_download_dir():
    return os.path.join(os.path.expanduser("~"), "Downloads", "UnsplashImages")


class UnsplashSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Unsplash 图片搜索工具 v2")
        self.root.geometry("1100x780")
        self.root.minsize(900, 620)
        self.download_dir = get_default_download_dir()
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        self.setup_ui()

    def setup_ui(self):
        # Tab bar
        tab_frame = tk.Frame(self.root, bg="#2C3E50", height=50)
        tab_frame.pack(fill=tk.X, side=tk.TOP)
        tab_frame.pack_propagate(False)

        self.tab_cn_btn = tk.Button(tab_frame, text="中文搜索",
                                     font=("Microsoft YaHei", 13, "bold"),
                                     bg="#27AE60", fg="white", padx=30, pady=8,
                                     relief=tk.FLAT, cursor="hand2",
                                     command=lambda: self.switch_tab("cn"))
        self.tab_cn_btn.pack(side=tk.LEFT, padx=(20, 5), pady=10)

        self.tab_en_btn = tk.Button(tab_frame, text="英文搜索",
                                     font=("Microsoft YaHei", 12),
                                     bg="#34495E", fg="#BDC3C7", padx=30, pady=8,
                                     relief=tk.FLAT, cursor="hand2",
                                     command=lambda: self.switch_tab("en"))
        self.tab_en_btn.pack(side=tk.LEFT, padx=5, pady=10)

        tk.Button(tab_frame, text="设置下载目录",
                  font=("Microsoft YaHei", 10),
                  bg="#34495E", fg="#BDC3C7", padx=15, pady=5,
                  relief=tk.FLAT, cursor="hand2",
                  command=self.choose_download_dir).pack(side=tk.RIGHT, padx=20, pady=10)

        # Chinese search panel
        self.cn_panel = tk.Frame(self.root, bg="#f0f4f8")
        self.cn_panel.pack(fill=tk.X, padx=15, pady=(12, 6))

        tk.Label(self.cn_panel, text="输入中文描述，我来帮你翻译并搜索：",
                 font=("Microsoft YaHei", 11), fg="#555", bg="#f0f4f8").pack(anchor="w", pady=(0, 5))

        cn_row = tk.Frame(self.cn_panel, bg="#f0f4f8")
        cn_row.pack(fill=tk.X)
        self.cn_entry = tk.Entry(cn_row, font=("Microsoft YaHei", 14), width=50)
        self.cn_entry.pack(side=tk.LEFT, padx=(0, 10), ipady=6)
        self.cn_entry.bind("<Return>", lambda e: self.search_cn())
        self.cn_search_btn = tk.Button(cn_row, text="翻译搜索",
                                        font=("Microsoft YaHei", 12, "bold"),
                                        bg="#27AE60", fg="white", padx=20, pady=4,
                                        relief=tk.FLAT, cursor="hand2",
                                        command=self.search_cn)
        self.cn_search_btn.pack(side=tk.LEFT)

        self.translate_preview = tk.Label(self.cn_panel, text="",
                                          font=("Microsoft YaHei", 10, "italic"),
                                          fg="#888", bg="#f0f4f8", anchor="w")
        self.translate_preview.pack(anchor="w", pady=(3, 0))

        # English search panel
        self.en_panel = tk.Frame(self.root, bg="#f0f4f8")

        tk.Label(self.en_panel, text="输入英文关键词搜索：",
                 font=("Microsoft YaHei", 11), fg="#555", bg="#f0f4f8").pack(anchor="w", pady=(12, 5))

        en_row = tk.Frame(self.en_panel, bg="#f0f4f8")
        en_row.pack(fill=tk.X)
        self.en_entry = tk.Entry(en_row, font=("Microsoft YaHei", 14), width=50)
        self.en_entry.pack(side=tk.LEFT, padx=(0, 10), ipady=6)
        self.en_entry.bind("<Return>", lambda e: self.search_en())
        self.en_search_btn = tk.Button(en_row, text="搜索",
                                        font=("Microsoft YaHei", 12, "bold"),
                                        bg="#2196F3", fg="white", padx=20, pady=4,
                                        relief=tk.FLAT, cursor="hand2",
                                        command=self.search_en)
        self.en_search_btn.pack(side=tk.LEFT)

        # Status bar
        self.status_label = tk.Label(self.root,
                                      text="支持中英文混合输入",
                                      font=("Microsoft YaHei", 10), fg="#666", pady=5)
        self.status_label.pack(fill=tk.X)

        # Main content
        content_frame = tk.Frame(self.root)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(4, 5))

        self.canvas = tk.Canvas(content_frame, bg="#ffffff", highlightthickness=0)
        scrollbar = ttk.Scrollbar(content_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.results_frame = tk.Frame(self.canvas, bg="#ffffff")
        self.canvas.create_window((0, 0), window=self.results_frame, anchor="nw")
        self.results_frame.bind("<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.bind_all("<MouseWheel>",
            lambda e: self.canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        # Bottom navigation
        nav_frame = tk.Frame(self.root, padx=15, pady=8, bg="#f5f5f5")
        nav_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.prev_btn = tk.Button(nav_frame, text="上一页",
                                   font=("Microsoft YaHei", 10), state=tk.DISABLED,
                                   command=self.prev_page, relief=tk.FLAT, cursor="hand2",
                                   bg="#607D8B", fg="white", padx=15, pady=4)
        self.prev_btn.pack(side=tk.LEFT, padx=10)

        self.page_label = tk.Label(nav_frame, text="第 1 / 1 页",
                                    font=("Microsoft YaHei", 10), fg="#555", bg="#f5f5f5")
        self.page_label.pack(side=tk.LEFT, padx=20)

        self.next_btn = tk.Button(nav_frame, text="下一页",
                                   font=("Microsoft YaHei", 10), state=tk.DISABLED,
                                   command=self.next_page, relief=tk.FLAT, cursor="hand2",
                                   bg="#607D8B", fg="white", padx=15, pady=4)
        self.next_btn.pack(side=tk.LEFT, padx=10)

        tk.Label(nav_frame, text=f"下载目录: {self.download_dir}",
                 font=("Microsoft YaHei", 8), fg="#999", bg="#f5f5f5").pack(side=tk.RIGHT)

    def switch_tab(self, tab):
        if tab == "cn":
            self.en_panel.pack_forget()
            self.cn_panel.pack(fill=tk.X, padx=15, pady=(12, 6))
            self.tab_cn_btn.config(bg="#27AE60", fg="white", font=("Microsoft YaHei", 13, "bold"))
            self.tab_en_btn.config(bg="#34495E", fg="#BDC3C7", font=("Microsoft YaHei", 12))
        else:
            self.cn_panel.pack_forget()
            self.en_panel.pack(fill=tk.X, padx=15, pady=(12, 6))
            self.tab_en_btn.config(bg="#2196F3", fg="white", font=("Microsoft YaHei", 13, "bold"))
            self.tab_cn_btn.config(bg="#34495E", fg="#BDC3C7", font=("Microsoft YaHei", 12))
        self.current_tab = tab
        self.clear_results()

    def clear_results(self):
        for widget in self.results_frame.winfo_children():
            widget.destroy()

    def choose_download_dir(self):
        folder = filedialog.askdirectory(initialdir=self.download_dir)
        if folder:
            self.download_dir = folder
            messagebox.showinfo("提示", f"下载目录已设置为：\n{folder}")

    def search_cn(self):
        global is_searching
        if is_searching:
            return
        query = self.cn_entry.get().strip()
        if not query:
            messagebox.showwarning("提示", "请输入中文描述")
            return
        is_searching = True
        self.cn_search_btn.config(state=tk.DISABLED, text="翻译中...")
        self.translate_preview.config(text="")
        self.status_label.config(text=f"正在翻译 \"{query}\" ...")

        def do():
            translated = translate_to_english(query)
            self.root.after(0, lambda: self.translate_preview.config(text=f"翻译结果: {translated}"))
            self.root.after(0, lambda: self.status_label.config(text=f"正在搜索 Unsplash: {translated} ..."))
            result = search_photos(translated, 1)
            if "error" in result:
                self.root.after(0, lambda: self.status_label.config(text=f"搜索失败: {result['error']}"))
            else:
                global search_results, current_page, total_pages
                search_results = result.get("results", [])
                total_pages = result.get("total_pages", 1)
                current_page = 1
                self.root.after(0, lambda: self.display_results(query, result.get("total", 0), translated))
            self.root.after(0, self.finish_search)

        threading.Thread(target=do, daemon=True).start()

    def search_en(self):
        global is_searching
        if is_searching:
            return
        query = self.en_entry.get().strip()
        if not query:
            messagebox.showwarning("提示", "请输入英文关键词")
            return
        is_searching = True
        self.en_search_btn.config(state=tk.DISABLED, text="搜索中...")
        self.status_label.config(text=f"正在搜索 \"{query}\" ...")

        def do():
            result = search_photos(query, 1)
            if "error" in result:
                self.root.after(0, lambda: self.status_label.config(text=f"搜索失败: {result['error']}"))
            else:
                global search_results, current_page, total_pages
                search_results = result.get("results", [])
                total_pages = result.get("total_pages", 1)
                current_page = 1
                self.root.after(0, lambda: self.display_results(query, result.get("total", 0), None))
            self.root.after(0, self.finish_search)

        threading.Thread(target=do, daemon=True).start()

    def finish_search(self):
        global is_searching
        is_searching = False
        self.cn_search_btn.config(state=tk.NORMAL, text="翻译搜索")
        self.en_search_btn.config(state=tk.NORMAL, text="搜索")
        self.prev_btn.config(state=tk.NORMAL if current_page > 1 else tk.DISABLED,
                             bg="#607D8B" if current_page > 1 else "#B0BEC5")
        self.next_btn.config(state=tk.NORMAL if current_page < total_pages else tk.DISABLED,
                            bg="#607D8B" if current_page < total_pages else "#B0BEC5")
        self.page_label.config(text=f"第 {current_page} / {total_pages} 页")

    def display_results(self, query, total, translated=None):
        self.clear_results()
        if not search_results:
            tk.Label(self.results_frame, text="未找到结果，请尝试其他关键词",
                     font=("Microsoft YaHei", 13), fg="#999", pady=60).pack()
            return
        info = f" (翻译: {translated})" if translated and translated != query else ""
        self.status_label.config(text=f"找到 {total} 个结果{info}，显示第 {len(search_results)} 个")
        cols = 4
        for idx, photo in enumerate(search_results):
            row = idx // cols
            col = idx % cols
            self.results_frame.columnconfigure(col, weight=1)
            self.create_card(row, col, photo)

    def create_card(self, row, col, photo):
        card = tk.Frame(self.results_frame, bg="white", relief=tk.RAISED, bd=1)
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

        img_label = tk.Label(card, bg="#e8e8e8", cursor="hand2", height=16)
        img_label.pack(fill=tk.BOTH, expand=True)

        thumb_url = photo.get("urls", {}).get("small", "")
        if thumb_url:
            threading.Thread(target=self.load_img, args=(thumb_url, img_label), daemon=True).start()

        info_frame = tk.Frame(card, bg="white")
        info_frame.pack(fill=tk.X, padx=5, pady=(3, 0))
        author = photo.get("user", {}).get("name", "Unknown")
        likes = photo.get("likes", 0)
        tk.Label(info_frame, text=f"By {author}  {likes} likes",
                 font=("Arial", 8), fg="#666", anchor="w").pack(anchor="w")

        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(fill=tk.X, padx=5, pady=3)
        for txt, color, cmd in [
            ("Copy", "#2196F3", lambda p=photo: self.copy_link(p)),
            ("Save", "#4CAF50", lambda p=photo: self.download_photo(p)),
            ("Open", "#FF9800", lambda p=photo: self.open_url(p)),
        ]:
            tk.Button(btn_frame, text=txt, font=("Arial", 9),
                      bg=color, fg="white", padx=8, pady=1,
                      relief=tk.FLAT, cursor="hand2",
                      command=cmd).pack(side=tk.LEFT, padx=2)

    def load_img(self, url, label):
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            from PIL import Image, ImageTk
            import io
            img = Image.open(io.BytesIO(resp.content))
            img = img.resize((220, 150), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            label.after(0, lambda: label.config(image=photo, height=150))
            label.image = photo
        except Exception:
            pass

    def copy_link(self, photo):
        url = photo.get("urls", {}).get("regular", "")
        self.root.clipboard_clear()
        self.root.clipboard_append(url)
        self.root.update()
        messagebox.showinfo("成功", f"链接已复制！\n\n{url}")

    def download_photo(self, photo):
        url = photo.get("urls", {}).get("full") or photo.get("urls", {}).get("regular", "")
        if not url:
            messagebox.showerror("错误", "无法获取图片链接")
            return
        photo_id = photo.get("id", "unknown")
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"unsplash_{photo_id}_{ts}.jpg"
        filepath = os.path.join(self.download_dir, filename)
        self.status_label.config(text=f"正在下载: {filename} ...")

        def do():
            ok = download_image(url, filepath)
            if ok:
                self.root.after(0, lambda: messagebox.showinfo("成功", f"已保存到：\n{filepath}"))
                self.root.after(0, lambda: self.status_label.config(text=f"下载完成: {filename}"))
            else:
                self.root.after(0, lambda: messagebox.showerror("错误", "下载失败"))
                self.root.after(0, lambda: self.status_label.config(text="下载失败"))

        threading.Thread(target=do, daemon=True).start()

    def open_url(self, photo):
        html = photo.get("links", {}).get("html", "")
        if html:
            import webbrowser
            webbrowser.open(html)

    def prev_page(self):
        global current_page
        if current_page > 1:
            self._do_page(current_page - 1)

    def next_page(self):
        global current_page, total_pages
        if current_page < total_pages:
            self._do_page(current_page + 1)

    def _do_page(self, page):
        global is_searching, current_page
        if is_searching:
            return
        is_searching = True
        self.cn_search_btn.config(state=tk.DISABLED, text="...")
        self.en_search_btn.config(state=tk.DISABLED, text="...")
        self.status_label.config(text=f"正在加载第 {page} 页 ...")

        query = (self.cn_entry.get().strip() if hasattr(self, 'current_tab') and self.current_tab == "cn" else self.en_entry.get().strip())

        def do():
            if hasattr(self, 'current_tab') and self.current_tab == "cn":
                translated = translate_to_english(query) if query else ""
                result = search_photos(translated, page)
                label = translated
            else:
                result = search_photos(query, page)
                label = None
            if "error" not in result:
                global search_results, total_pages
                search_results = result.get("results", [])
                total_pages = result.get("total_pages", 1)
                current_page = page
                self.root.after(0, lambda: self.display_results(query, result.get("total", 0), label))
            self.root.after(0, self.finish_search)

        threading.Thread(target=do, daemon=True).start()


def main():
    root = tk.Tk()
    app = UnsplashSearchApp(root)
    app.current_tab = "cn"
    root.mainloop()


if __name__ == "__main__":
    main()
