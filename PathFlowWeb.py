# -*- coding: utf-8 -*-
import streamlit as st
from urllib.parse import urljoin, urlparse
import os
import pandas as pd

# --- ページ設定 (Page Config) ---
st.set_page_config(page_title="PathFlow Pro", page_icon="🌐", layout="wide")

# --- パス変換ロジック ---
def to_relative(base, absolute):
    try:
        if urlparse(base).netloc != urlparse(absolute).netloc: return absolute
        rel = os.path.relpath(urlparse(absolute).path, os.path.dirname(urlparse(base).path))
        return rel.replace("\\", "/")
    except: return absolute

# --- UI ヘッダー ---
st.title("🌐 PathFlow Pro")
st.markdown("ファイル内のURLパスを基準URLをもとに一括で双方向変換（相対 ↔ 絶対）します。")
st.divider()

# --- メイン画面のレイアウト (2カラム) ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("⚙️ 変換設定")
    base_url = st.text_input("1. 基準URL (Base URL)", "https://example.com/folder/")
    mode = st.selectbox("2. 変換モード", ["相対 -> 絶対 (Relative to Absolute)", "絶対 -> 相対 (Absolute to Relative)"])
    targets = st.text_input("3. 変換対象キーワード (カンマ区切り)", "img/,index2.html")

with col2:
    st.subheader("📂 ファイルアップロード")
    uploaded_file = st.file_uploader("ここにファイルをドラッグ＆ドロップ", type=["html", "css", "js", "txt"])

# --- 実行処理 ---
st.markdown("<br>", unsafe_allow_html=True)
if uploaded_file and st.button("🚀 変換を実行する", use_container_width=True):
    with st.spinner("変換中..."):
        content = uploaded_file.getvalue().decode("utf-8")
        target_list = [t.strip() for t in targets.split(",") if t.strip()]
        logs = []

        # 置換処理
        for t in target_list:
            res = urljoin(base_url, t) if "相対 -> 絶対" in mode else to_relative(base_url, t)
            if t in content:
                content = content.replace(t, res)
                logs.append({"ターゲット": t, "変換後のパス": res, "ステータス": "✅ 置換完了"})
            else:
                logs.append({"ターゲット": t, "変換後のパス": res, "ステータス": "❓ 未検出"})

        st.success("✅ ファイルの変換が完了しました！下のボタンからダウンロードしてください。")

        # 結果表示とダウンロード
        res_col1, res_col2 = st.columns([1.5, 1])
        with res_col1:
            st.dataframe(pd.DataFrame(logs), use_container_width=True)
        with res_col2:
            st.download_button(
                label=f"💾 変換済みファイルを保存 (pf_{uploaded_file.name})",
                data=content,
                file_name=f"pf_{uploaded_file.name}",
                mime="text/plain",
                use_container_width=True
            )