# -*- coding: utf-8 -*-
import streamlit as st
from urllib.parse import urljoin
import pandas as pd
import zipfile
import io

# --- ページ設定 ---
st.set_page_config(page_title="PathFlow Pro 2.0", page_icon="🚀", layout="wide")

st.title("🚀 PathFlow Pro 2.0")
st.markdown("複数のファイルを一括変換し、ZIPでまとめてダウンロードできるプロ仕様バージョンです。")
st.divider()

# --- 💡 アップグレード: プリセット（お気に入り）機能 ---
if "base_url" not in st.session_state: st.session_state.base_url = "https://example.com/folder/"
if "targets" not in st.session_state: st.session_state.targets = "img/, index2.html"

def set_preset_1():
    st.session_state.base_url = "https://example.com/sample1/"
    st.session_state.targets = "img/, index2.html"

def set_preset_2():
    st.session_state.base_url = "https://example.com/sample2/"
    st.session_state.targets = "img/, index2.html"

st.markdown("**💡 よく使う設定（クリックで一発入力）**")
col_preset1, col_preset2, _ = st.columns([1, 1, 4])
# ボタンの名前を「sample 1」「sample 2」に変更！
with col_preset1: st.button("📁 sample 1", on_click=set_preset_1, use_container_width=True)
with col_preset2: st.button("🛒 sample 2", on_click=set_preset_2, use_container_width=True)
st.markdown("<br>", unsafe_allow_html=True)

# --- メイン画面 ---
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("⚙️ 変換設定")
    base_url = st.text_input("1. 基準URL (Base URL)", key="base_url")
    mode = st.selectbox("2. 変換モード", ["相対 -> 絶対 (Relative to Absolute)", "絶対 -> 相対 (Absolute to Relative)"])
    targets = st.text_input("3. 変換対象キーワード (カンマ区切り)", key="targets")

with col2:
    st.subheader("📂 ファイル一括アップロード")
    # 💡 アップグレード: 複数ファイル選択可能に！ (accept_multiple_files=True)
    uploaded_files = st.file_uploader("ここに複数のファイルをドラッグ＆ドロップ", type=["html", "css", "js", "txt"], accept_multiple_files=True)

st.markdown("<br>", unsafe_allow_html=True)

# --- 実行処理 ---
if uploaded_files and st.button("🚀 一括変換を実行する", use_container_width=True):
    if not targets.strip():
        st.warning("⚠️ 変換対象キーワードを入力してください。")
    else:
        with st.spinner("全ファイルを一括変換中..."):
            target_list = [t.strip() for t in targets.split(",") if t.strip()]
            all_logs = []
            
            # 💡 アップグレード: ZIPファイル作成の準備
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                
                # アップロードされた全ファイルを順番に処理
                for uploaded_file in uploaded_files:
                    content = uploaded_file.getvalue().decode("utf-8")
                    
                    for t in target_list:
                        if "相対 -> 絶対" in mode:
                            search_str = t
                            replace_str = urljoin(base_url, t)
                        else:
                            search_str = urljoin(base_url, t)
                            replace_str = t

                        if search_str in content:
                            content = content.replace(search_str, replace_str)
                            all_logs.append({"ファイル名": uploaded_file.name, "ターゲット": t, "検索文字列": search_str, "変換後": replace_str, "状態": "✅ 完了"})
                        else:
                            all_logs.append({"ファイル名": uploaded_file.name, "ターゲット": t, "検索文字列": search_str, "変換後": "-", "状態": "❓ 未検出"})

                    # 変換したファイルデータをZIPのなかに保存
                    zip_file.writestr(f"pf_{uploaded_file.name}", content)

            st.success(f"✅ {len(uploaded_files)}個のファイル一括変換が完了しました！")

            res_col1, res_col2 = st.columns([1.5, 1])
            with res_col1:
                # ログ表示もファイル名付きで分かりやすく！
                st.dataframe(pd.DataFrame(all_logs), use_container_width=True)
            with res_col2:
                # 💡 アップグレード: ZIPで一括ダウンロード！
                st.download_button(
                    label="📦 変換済みファイルをZIPで一括ダウンロード",
                    data=zip_buffer.getvalue(),
                    file_name="PathFlow_Converted.zip",
                    mime="application/zip",
                    use_container_width=True
                )
