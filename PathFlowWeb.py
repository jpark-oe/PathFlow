# -*- coding: utf-8 -*-
import streamlit as st
from urllib.parse import urljoin
import pandas as pd
import zipfile
import io

st.set_page_config(page_title="PathFlow Pro 2.0", page_icon="🚀", layout="wide")

st.title("🚀 PathFlow Pro 2.0 (Ultimate Edition)")
st.markdown("複数のファイルを一括変換し、ZIPでまとめてダウンロードできるプロ仕様バージョンです。")
st.divider()

# --- 💡 プリセット機能 (FREEタブ用) ---
if "free_base_url" not in st.session_state: st.session_state.free_base_url = "https://example.com/folder/"
if "free_targets" not in st.session_state: st.session_state.free_targets = "img/, index2.html"

def set_preset_1():
    st.session_state.free_base_url = "https://example.com/sample1/"
    st.session_state.free_targets = "img/, index2.html"

def set_preset_2():
    st.session_state.free_base_url = "https://example.com/sample2/"
    st.session_state.free_targets = "img/, index2.html"

# --- ⚙️ 共通の変換処理関数 ---
def run_conversion(base_url, mode, targets, uploaded_files):
    if not targets.strip():
        st.warning("⚠️ 変換対象キーワードを入力してください。")
        return

    with st.spinner("全ファイルを一括変換中..."):
        target_list = [t.strip() for t in targets.split(",") if t.strip()]
        all_logs = []
        
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
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

                zip_file.writestr(uploaded_file.name, content)

        st.success(f"✅ {len(uploaded_files)}個のファイル一括変換が完了しました！")

        res_col1, res_col2 = st.columns([1.5, 1])
        with res_col1:
            st.dataframe(pd.DataFrame(all_logs), use_container_width=True)
        with res_col2:
            st.download_button(
                label="📦 変換済みファイルをZIPでダウンロード",
                data=zip_buffer.getvalue(),
                file_name="PathFlow_Converted.zip",
                mime="application/zip",
                use_container_width=True
            )

# --- 📁 タブの作成 ---
tab1, tab2 = st.tabs(["🆓 FREE", "🏢 長谷工提携法人"])

# ==========================================
# TAB 1: FREE (自由入力＆プリセット)
# ==========================================
with tab1:
    st.markdown("**💡 よく使う設定（クリックで一発入力）**")
    col_preset1, col_preset2, _ = st.columns([1, 1, 4])
    with col_preset1: st.button("📁 sample 1", on_click=set_preset_1, key="btn_p1", use_container_width=True)
    with col_preset2: st.button("🛒 sample 2", on_click=set_preset_2, key="btn_p2", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col1_1, col1_2 = st.columns([1, 1.2])
    with col1_1:
        st.subheader("⚙️ 変換設定 (FREE)")
        base_url_free = st.text_input("1. 基準URL (Base URL)", key="free_base_url")
        mode_free = st.selectbox("2. 変換モード", ["相対 -> 絶対 (Relative to Absolute)", "絶対 -> 相対 (Absolute to Relative)"], key="mode_free")
        targets_free = st.text_input("3. 変換対象キーワード (カンマ区切り)", key="free_targets")
    with col1_2:
        st.subheader("📂 ファイル一括アップロード")
        uploaded_files_free = st.file_uploader("ここに複数のファイルをドラッグ＆ドロップ", type=["html", "css", "js", "txt"], accept_multiple_files=True, key="up_free")

    if uploaded_files_free and st.button("🚀 FREE設定で一括変換を実行", use_container_width=True, key="exec_free"):
        run_conversion(base_url_free, mode_free, targets_free, uploaded_files_free)

# ==========================================
# TAB 2: 長谷工提携法人 (URL固定 + 追加パス)
# ==========================================
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    col2_1, col2_2 = st.columns([1, 1.2])
    
    with col2_1:
        st.subheader("⚙️ 変換設定 (長谷工提携法人)")
        
        # 💡 アップグレード: URLを「固定部分」と「入力部分」に分割！
        st.markdown("**1. 基準URL** (固定部分 + 追加パス)")
        url_col1, url_col2 = st.columns([2, 1])
        with url_col1:
            st.text_input("固定部分", value="https://www.haseko-teikei.jp/mailmagazine/", disabled=True, label_visibility="collapsed")
        with url_col2:
            haseko_suffix = st.text_input("追加部分", placeholder="例: 2512/", label_visibility="collapsed", key="haseko_suffix")
        
        # 内部で2つの文字列を合体させる（最後に '/' がなければ自動追加する親切設計）
        base_url_haseko = "https://www.haseko-teikei.jp/mailmagazine/" + haseko_suffix.strip()
        if not base_url_haseko.endswith('/'):
            base_url_haseko += '/'
            
        # 最終的にどんなURLで変換されるか確認用テキストを表示
        st.caption(f"🔗 **合体後のURL:** `{base_url_haseko}`")
        
        mode_haseko = st.selectbox("2. 変換モード", ["相対 -> 絶対 (Relative to Absolute)", "絶対 -> 相対 (Absolute to Relative)"], key="mode_haseko")
        targets_haseko = st.text_input("3. 変換対象キーワード (カンマ区切り)", value="img/, index2.html", key="targets_haseko")
    
    with col2_2:
        st.subheader("📂 ファイル一括アップロード")
        uploaded_files_haseko = st.file_uploader("ここに複数のファイルをドラッグ＆ドロップ", type=["html", "css", "js", "txt"], accept_multiple_files=True, key="up_haseko")

    if uploaded_files_haseko and st.button("🚀 長谷工設定で一括変換を実行", use_container_width=True, key="exec_haseko"):
        run_conversion(base_url_haseko, mode_haseko, targets_haseko, uploaded_files_haseko)
