# -*- coding: utf-8 -*-
import streamlit as st
from urllib.parse import urljoin
import pandas as pd

st.set_page_config(page_title="PathFlow Pro", page_icon="🌐", layout="wide")

st.title("🌐 PathFlow Pro (Web Version)")
st.markdown("ファイル内のURLパスを基準URLをもとに一括で双方向変換（相対 ↔ 絶対）します。")
st.divider()

col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("⚙️ 変換設定")
    base_url = st.text_input("1. 基準URL (Base URL)", "https://example.com/folder/")
    mode = st.selectbox("2. 変換モード", ["相対 -> 絶対 (Relative to Absolute)", "絶対 -> 相対 (Absolute to Relative)"])
    targets = st.text_input("3. 変換対象キーワード (カンマ区切り)", "img/, index2.html")

with col2:
    st.subheader("📂 ファイルアップロード")
    uploaded_file = st.file_uploader("ここにファイルをドラッグ＆ドロップ", type=["html", "css", "js", "txt"])

st.markdown("<br>", unsafe_allow_html=True)

if uploaded_file and st.button("🚀 変換を実行する", use_container_width=True):
    if not targets.strip():
        st.warning("⚠️ 変換対象キーワードを入力してください。")
    else:
        with st.spinner("変換中..."):
            content = uploaded_file.getvalue().decode("utf-8")
            target_list = [t.strip() for t in targets.split(",") if t.strip()]
            logs = []

            for t in target_list:
                if "相対 -> 絶対" in mode:
                    # 相対 -> 絶対: 'img/' を 'https://.../img/' に置換
                    search_str = t
                    replace_str = urljoin(base_url, t)
                else:
                    # 絶対 -> 相対: 'https://.../img/' を 'img/' に置換 (基準URLを削除)
                    search_str = urljoin(base_url, t)
                    replace_str = t

                # ファイル内に該当する文字列があるか確認して置換
                if search_str in content:
                    content = content.replace(search_str, replace_str)
                    logs.append({"ターゲット": t, "検索した文字列": search_str, "変換後のパス": replace_str, "ステータス": "✅ 置換完了"})
                else:
                    logs.append({"ターゲット": t, "検索した文字列": search_str, "変換後のパス": "-", "ステータス": "❓ 未検出"})

            st.success("✅ ファイルの変換が完了しました！下のボタンからダウンロードしてください。")

            res_col1, res_col2 = st.columns([1.5, 1])
            with res_col1:
                # ログをデータフレームで綺麗に表示
                st.dataframe(pd.DataFrame(logs), use_container_width=True)
            with res_col2:
                st.download_button(
                    label=f"💾 変換済みファイルを保存 (pf_{uploaded_file.name})",
                    data=content,
                    file_name=f"pf_{uploaded_file.name}",
                    mime="text/plain",
                    use_container_width=True
                )
