# GitHub Actions 在线打包 macOS 应用

## 使用方法（2分钟完成）

### 步骤 1：创建 GitHub 仓库
1. 访问 https://github.com/new
2. 仓库名：`unsplash-search`
3. 选择 **Private**（私密）
4. 点击 **Create repository**

### 步骤 2：上传代码
把 `unsplash-search` 文件夹里的所有内容上传到 GitHub：

**方式 A - 网页上传（最简单）：**
1. 进入新建的 GitHub 仓库
2. 点击 **"uploading an existing file"**
3. 拖拽或选择以下文件上传：
   - `app.py`
   - `config.py`
   - `.github/workflows/build-macos.yml`（整个文件夹结构）

**方式 B - 命令行（如果你会用 git）：**
```bash
cd unsplash-search
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/unsplash-search.git
git push -u origin main
```

### 步骤 3：触发自动打包
1. 在 GitHub 仓库页面，点击 **Actions** 标签
2. 选择 **"Build macOS App"** 工作流
3. 点击 **"Run workflow"** → **"Run workflow"**
4. 等待约 3-5 分钟

### 步骤 4：下载应用
打包完成后：
1. 点击 **Actions** → 最新的运行记录
2. 页面底部 **Artifacts** 区域
3. 下载 `UnsplashSearch-macOS.zip`
4. 解压得到 `UnsplashSearch.app`

---

## 自动触发
每次你更新代码并 push 到 GitHub 时，会自动重新打包。

## 文件说明
- `.github/workflows/build-macos.yml` - GitHub Actions 配置文件
- 云端使用 macOS 虚拟机打包，完全免费
