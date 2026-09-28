import argparse
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


def try_convert(tgs_path: Path, out_path: Path):
    """主方案:python-lottie 库"""
    cmd = ["lottie_convert.py", str(tgs_path), str(out_path)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode == 0:
            return True, ""
        return False, result.stderr.strip()
    except Exception as e:
        return False, str(e)


def try_convert_rlottie(tgs_path: Path, out_path: Path):
    """备用方案:rlottie(Telegram 官方同款渲染引擎)"""
    try:
        from rlottie_python import LottieAnimation
    except ImportError:
        return False, "未安装 rlottie-python,跳过备用方案"
    try:
        with LottieAnimation.from_tgs(str(tgs_path)) as anim:
            anim.save_animation(str(out_path))
        return True, ""
    except Exception as e:
        return False, str(e)


def convert_one(tgs_path: Path, out_dir: Path, retries: int):
    """先用主方案转,失败重试;仍失败则换 rlottie 备用方案"""
    out_path = out_dir / (tgs_path.stem + ".gif")
    last_err = ""
    for attempt in range(retries + 1):
        ok, err = try_convert(tgs_path, out_path)
        if ok:
            tag = "OK" if attempt == 0 else f"OK(重试{attempt}次后成功)"
            return tgs_path, True, tag, ""
        last_err = err

    ok, err2 = try_convert_rlottie(tgs_path, out_path)
    if ok:
        return tgs_path, True, "OK(rlottie备用方案)", ""

    return tgs_path, False, "FAIL", f"主方案: {last_err}\n备用方案: {err2}"


def main():
    parser = argparse.ArgumentParser(description="批量将 .tgs 转为 .gif")
    parser.add_argument("input_dir", help="存放 .tgs 文件的文件夹")
    parser.add_argument("-o", "--output", default=None, help="输出文件夹,默认与输入相同")
    parser.add_argument("-w", "--workers", type=int, default=4, help="并发线程数,默认 4")
    parser.add_argument("-r", "--retries", type=int, default=1, help="单文件失败后重试次数,默认 1")
    args = parser.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.output) if args.output else in_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    tgs_files = list(in_dir.glob("*.tgs"))
    if not tgs_files:
        print(f"在 {in_dir} 中没有找到 .tgs 文件")
        return

    print(f"找到 {len(tgs_files)} 个文件,开始转换(并发数: {args.workers}, 失败重试: {args.retries}次)...")

    ok_count, fail_list = 0, []
    log_path = out_dir / "conversion_errors.log"

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(convert_one, f, out_dir, args.retries): f for f in tgs_files}
        for future in as_completed(futures):
            path, success, tag, err = future.result()
            if success:
                ok_count += 1
                print(f"[{tag}] {path.name}")
            else:
                fail_list.append((path.name, err))
                print(f"[FAIL] {path.name}")

    print(f"\n完成: 成功 {ok_count} 个, 失败 {len(fail_list)} 个")

    if fail_list:
        print("\n失败文件清单:")
        for name, _ in fail_list:
            print(f"  - {name}")

        with open(log_path, "w", encoding="utf-8") as f:
            f.write(f"转换时间: {datetime.now()}\n")
            f.write(f"成功 {ok_count} 个, 失败 {len(fail_list)} 个\n\n")
            for name, err in fail_list:
                f.write(f"文件: {name}\n错误详情:\n{err}\n{'-'*50}\n")

        print(f"\n详细错误已写入: {log_path}")
        print("(这些大概率是动画用了库不支持的特殊效果,并非操作问题)")


if __name__ == "__main__":
    main()
