#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
用法：bash install.sh [--claude] [--prefix 目录]

默认下载安装到 ~/.agents/skills。
  --claude       同时将文件硬链接到 ~/.claude/skills（须位于同一文件系统）
  --prefix 目录  使用指定目录代替用户目录
  -h, --help     显示帮助
EOF
}

die() {
  printf '安装失败：%s\n' "$1" >&2
  exit 1
}

install_prefix="${HOME:?未设置 HOME，无法确定用户技能目录}"
with_claude=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --claude) with_claude=1; shift ;;
    --prefix)
      [[ $# -ge 2 && -n "$2" ]] || die '--prefix 需要目录参数'
      install_prefix="$2"
      shift 2
      ;;
    -h|--help) usage; exit 0 ;;
    *) die "未知参数：$1" ;;
  esac
done
[[ -d "$install_prefix" ]] || die "安装所在目录不存在：$install_prefix"
install_prefix="$(cd -- "$install_prefix" && pwd -P)"
canonical_root="$install_prefix/.agents/skills"
claude_root="$install_prefix/.claude/skills"

# 不依赖脚本所在目录，支持通过 curl | bash 从标准输入执行。
archive_url="${SUPERWORK_ARCHIVE_URL:-https://codeload.github.com/BryanHoo/superwork/tar.gz/refs/heads/main}"
download_dir="$(mktemp -d "${TMPDIR:-/tmp}/superwork-install.XXXXXX")"
trap 'rm -rf -- "$download_dir"' EXIT
curl -fsSL "$archive_url" -o "$download_dir/source.tar.gz" || die '下载技能失败'
tar -xzf "$download_dir/source.tar.gz" -C "$download_dir" --strip-components=1 || die '解包技能失败'
skills_root="$download_dir/skills"
[[ -f "$skills_root/_shared/repository.py" ]] || die "下载内容缺少 _shared 共享依赖"

# _shared 没有 SKILL.md，仍须与所有技能一同复制，确保共享导入和模板引用可用。
sources=("$skills_root/_shared")
for source in "$skills_root"/*; do
  if [[ -f "$source/SKILL.md" ]]; then
    sources+=("$source")
  fi
done
[[ ${#sources[@]} -gt 1 ]] || die '下载内容中未找到技能'

trees_match() {
  # 运行工作流会生成 Python 缓存；这些文件不影响是否已安装相同版本。
  [[ -d "$2" && ! -L "$2" ]] && diff -qr -x '__pycache__' "$1" "$2" >/dev/null 2>&1
}

hardlinks_match() {
  trees_match "$1" "$2" || return 1
  local file relative
  while IFS= read -r -d '' file; do
    relative="${file#"$1"/}"
    [[ ! -L "$2/$relative" && "$file" -ef "$2/$relative" ]] || return 1
  done < <(find "$1" -name '__pycache__' -prune -o -type f -print0)
}

has_conflicts=0
report_conflict() {
  printf '路径已被占用或内容不一致：%s\n' "$1" >&2
  has_conflicts=1
}

# 写入前预检全部目录和技能；Claude 的已有文件必须确实共享默认安装的 inode。
directories=("$canonical_root")
if [[ "$with_claude" -eq 1 ]]; then
  directories+=("$claude_root")
fi
for directory in "${directories[@]}"; do
  parent="$directory"
  while [[ ! -d "$parent" ]]; do
    if [[ -e "$parent" || -L "$parent" ]]; then
      report_conflict "$parent"
      break
    fi
    parent="$(dirname -- "$parent")"
  done
  for source in "${sources[@]}"; do
    name="${source##*/}"
    target="$directory/$name"
    if [[ -e "$target" || -L "$target" ]]; then
      if [[ "$directory" == "$canonical_root" ]]; then
        trees_match "$source" "$target" || report_conflict "$target"
      else
        if ! trees_match "$source" "$canonical_root/$name" || ! hardlinks_match "$canonical_root/$name" "$target"; then
          report_conflict "$target"
        fi
      fi
    fi
  done
done
[[ "$has_conflicts" -eq 0 ]] || die '未写入任何安装条目，请先检查并处理上述冲突'

# 复制完整技能目录，安装结果不依赖临时下载目录或本地源码仓库。
mkdir -p -- "$canonical_root"
for source in "${sources[@]}"; do
  target="$canonical_root/${source##*/}"
  if [[ ! -d "$target" ]]; then
    cp -R -- "$source" "$target"
  fi
done
printf '已安装：%s\n' "$canonical_root"

if [[ "$with_claude" -eq 1 ]]; then
  for source in "${sources[@]}"; do
    name="${source##*/}"
    canonical="$canonical_root/$name"
    target="$claude_root/$name"
    if [[ -d "$target" ]]; then
      continue
    fi
    # 目录不能直接创建硬链接：重建目录结构，逐文件硬链接并跳过运行时缓存。
    while IFS= read -r -d '' entry; do
      relative="${entry#"$canonical"}"
      if [[ -d "$entry" ]]; then
        mkdir -p -- "$target$relative"
      elif [[ -f "$entry" ]]; then
        ln -- "$entry" "$target$relative" || die '创建硬链接失败，请确保 .agents 和 .claude 位于同一文件系统'
      fi
    done < <(find "$canonical" -name '__pycache__' -prune -o -print0)
  done
  printf '已为 Claude Code 创建文件硬链接：%s\n' "$claude_root"
else
  printf '如需同时用于 Claude Code，可重新运行安装命令并加上 --claude。\n'
fi
