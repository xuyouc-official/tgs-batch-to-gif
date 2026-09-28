# tgs-batch-to-gif

批量将 Telegram 动态表情包(`.tgs`)转换为 `.gif` 的多线程 Python 脚本,专门针对 **Android + Termux** 环境整理了完整的安装流程。

## 特性

- 多线程并发转换,速度可调(`-w`)
- 转换失败自动重试(`-r`)
- 失败文件汇总输出,详细报错写入 `conversion_errors.log`,不会刷屏
- 可选备用渲染方案:若环境中装有 `rlottie-python`,主方案失败的文件会自动改用 rlottie 再试一次(仅桌面系统可用)

## 在 Termux(Android)上使用

### 1. 安装环境

从 [F-Droid](https://f-droid.org) 或 GitHub 安装最新版 Termux(不建议用 Google Play 版本),然后依次执行:

```bash
pkg update && pkg upgrade
pkg install python libjpeg-turbo
pip install Pillow
pip install lottie cairosvg
```

> 如果安装 Pillow 时报 `The headers or library files could not be found for jpeg`,就是缺少 `libjpeg-turbo`,先执行 `pkg install libjpeg-turbo` 再重试。

### 2. 让 Termux 访问手机存储

```bash
termux-setup-storage
```

在弹出的权限申请中点"允许"。

### 3. 放置脚本并运行

将 `batch_tgs_to_gif.py` 放到手机"下载"目录,然后:

```bash
cp ~/storage/downloads/batch_tgs_to_gif.py ~/
python batch_tgs_to_gif.py ~/storage/downloads/stickers
```

## 参数说明

```
python batch_tgs_to_gif.py <输入文件夹> [-o 输出文件夹] [-w 线程数] [-r 重试次数]
```

| 参数 | 说明 | 默认值 |
| --- | --- | --- |
| `input_dir` | 存放 `.tgs` 文件的文件夹 | 必填 |
| `-o`, `--output` | 输出文件夹 | 与输入文件夹相同 |
| `-w`, `--workers` | 并发线程数,建议不超过 CPU 核心数 | 4 |
| `-r`, `--retries` | 单个文件失败后的重试次数 | 1 |

示例:

```bash
python batch_tgs_to_gif.py ~/storage/downloads/stickers -o ~/storage/downloads/output -w 8 -r 2
```

## 已知限制(请务必阅读)

手机端使用的转换库 [python-lottie](https://pypi.org/project/lottie/) 是纯 Python 实现,对部分 Lottie 特效支持不完整。实测 120 个表情包中:

- 约 **6%** 转换直接失败(库内部报除零错误,通常与路径裁剪 Trim Path 有关)
- 部分转换"成功"但**画面不正确**,例如:
  - 遮罩(mask)失效,本该被裁剪的元素跑到了外面
  - 图层混合模式(blend mode)不支持,发光的屏幕变成黑块

如果你对渲染准确度要求高,建议在电脑上使用基于 [rlottie](https://github.com/Samsung/rlottie)(Telegram 官方同款渲染引擎)的工具重新转换,例如:

- [ed-asriyan/lottie-converter](https://github.com/ed-asriyan/lottie-converter)
- [FHPythonUtils/PyRlottie](https://github.com/FHPythonUtils/PyRlottie)

> `rlottie-python` 目前**无法在 Android/Termux 上安装**(构建工具直接报 `Unsupported platform: Android`),因此备用方案仅在桌面系统生效。

## 常见问题

**Q:运行时突然刷出一大串报错?**
A:旧版本会把失败文件的完整报错打印到屏幕。新版本已改为只显示文件名,详细信息写入 `conversion_errors.log`。

**Q:怎么找出哪些文件转换失败了?**
A:运行结束时会列出失败文件清单;也可以在输出目录里对比,没有同名 `.gif` 的 `.tgs` 就是失败的。

**Q:线程数设多少合适?**
A:一般设为手机 CPU 核心数即可(旗舰机 8 核可用 `-w 8`),再高提升不明显,还可能发热卡顿。

## 许可证

[MIT](LICENSE)
