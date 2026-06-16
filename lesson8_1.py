import streamlit as st
import base64
import os
from datetime import datetime

# ページの基本設定
st.set_page_config(page_title="おにぎりメーカー", page_icon="🍙", layout="wide")

# フォントサイズを大きくするためのカスタムCSS
st.markdown("""
    <style>
    label { font-size: 1.5rem !important; font-weight: bold !important; }
    .stMarkdown p { font-size: 1.3rem; }
    .stButton button p { font-size: 1.3rem !important; }
    </style>
    """, unsafe_allow_html=True)

# セッション状態の初期化（アーカイブ保存用）
if 'onigiri_archive' not in st.session_state:
    st.session_state['onigiri_archive'] = []

st.title("🍙 おにぎりメーカー")
st.write("形・具・飾りを選んで、自分だけのおにぎりをデザイン。メモと一緒に思い出に残しましょう。")

# ---------------------------------------------------------
# 画像アセットの設定 (imagesフォルダ内のファイル名と対応させてください)
# ---------------------------------------------------------
IMAGE_DIR = "images"

SHAPE_MAP = {
    "しお": "sio.PNG",
    "焼き": "yaki.PNG",
    "ケチャップ": "ketya.PNG",
    "枝豆": "edamame.PNG",
    "ゆかり": "yukari.PNG"
}

FILLING_MAP = {
    "うめ": "ume.PNG",
    "さけ": "sake.PNG",
    "こんぶ": "konnbu.PNG",
    "明太子": "menntaiko.PNG",
    "ツナマヨ": "tunamayo.PNG",
    "えび天": "ebitenn.PNG",
    "チーズ": "tiizu.PNG",
}

GARNISH_MAP = {
    "のり１": "nori_1.PNG",
    "たまご": "tamago.PNG",
    "葉１": "ha_1.PNG",
    "のり２": "nori_2.PNG",
    "葉２": "ha_2.PNG"
}

@st.cache_data
def get_image_base64(path):
    """ローカル画像をBase64文字列に変換する"""
    if not path or not os.path.exists(path):
        return ""
    with open(path, "rb") as f:
        data = f.read()
    encoded = base64.b64encode(data).decode()
    # 拡張子を考慮してmimeタイプを生成（PNG/JPG対応）
    return f"data:image/png;base64,{encoded}"

def render_onigiri_canvas(shape_key, filling_key, garnish_key, bg_color, size=300):
    """HTMLとCSSを使用して画像を重ね合わせてキャンバスを作成する"""
    shape_path = os.path.join(IMAGE_DIR, "onigiri", SHAPE_MAP.get(shape_key, ""))
    filling_path = os.path.join(IMAGE_DIR, "guzai", FILLING_MAP.get(filling_key, ""))
    garnish_file = GARNISH_MAP.get(garnish_key, "") if garnish_key else ""
    garnish_path = os.path.join(IMAGE_DIR, "kazari", garnish_file) if garnish_file else ""

    # 画像をBase64に変換
    shape_base64 = get_image_base64(shape_path)
    filling_base64 = get_image_base64(filling_path)
    garnish_base64 = get_image_base64(garnish_path)

    html_code = f"""
    <div style="position: relative; width: {size}px; height: {size}px; background-color: {bg_color}; border-radius: 15px; overflow: hidden; margin: auto; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        {f'<img src="{shape_base64}" style="position: absolute; top: 0; left: 0; width: 100%; z-index: 1;">' if shape_base64 else ''}
        {f'<img src="{filling_base64}" style="position: absolute; top: 0; left: 0; width: 100%; z-index: 2;">' if filling_base64 else ''}
        {f'<img src="{garnish_base64}" style="position: absolute; top: 0; left: 0; width: 100%; z-index: 3;">' if garnish_base64 else ''}
    </div>
    """
    return html_code

# ---------------------------------------------------------
# 1. ユーザー入力セクション (Input)
# ---------------------------------------------------------
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("🛠️ デザイン設計")
    shape = st.selectbox("1. 形を選ぶ", list(SHAPE_MAP.keys()))
    filling = st.radio("2. 中身（具材）", list(FILLING_MAP.keys()), horizontal=True)
    garnish = st.selectbox("3. 外側の飾り", list(GARNISH_MAP.keys()))

    card_color = st.color_picker("カードの背景色を選択", "#F0F2F6")

    st.subheader("✍️ 記録の設定")
    title = st.text_input("作品名", value="今日の一膳")
    memo = st.text_area("一言メモ", placeholder="今日のおにぎりは上手く握れた！")

    if st.button("完成！アーカイブに保存する", type="primary", use_container_width=True):
        # ---------------------------------------------------------
        # 2. 処理セクション (Process)
        # ---------------------------------------------------------
        new_entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": title,
            "design": f"{shape} / {filling} / {garnish}",
            "shape": shape,
            "filling": filling,
            "garnish": garnish,
            "memo": memo,
            "color": card_color
        }
        # リストの先頭に追加（新しい順）
        st.session_state['onigiri_archive'].insert(0, new_entry)
        st.toast("アーカイブに保存されました！")
        st.balloons()

with col2:
    st.markdown("<h3 style='text-align: center;'>🖼️ キャンバス（プレビュー）</h3>", unsafe_allow_html=True)
    # リアルタイムでプレビューを描画
    canvas_html = render_onigiri_canvas(shape, filling, garnish, card_color, size=400)
    st.markdown(canvas_html, unsafe_allow_html=True)
    st.markdown(f'<div style="width: 400px; margin: auto; color: #808495; font-size: 1.2rem; margin-top: 0.8rem; text-align: center;">※設定を変更すると、リアルタイムでおにぎりが変化します。</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 3. 結果表示セクション (Display)
# ---------------------------------------------------------
st.divider()
st.header("🗄️ おにぎりアーカイブ")

if not st.session_state['onigiri_archive']:
    st.info("まだ保存されたアーカイブはありません。上のボタンを押して作成してみましょう！")
else:
    # 2カラムのグリッド表示に変更してバランスを整える
    archive_cols = st.columns(2)
    for i, entry in enumerate(st.session_state['onigiri_archive']):
        # インデックスに応じて左右のカラムに振り分け
        with archive_cols[i % 2]:
            # HTML/CSSを使用してカスタムカードを作成
            # アーカイブ内でも画像を再描画
            archive_canvas = render_onigiri_canvas(
                entry['shape'], entry['filling'], entry['garnish'], 
                "transparent", size=150
            )
            
            st.markdown(
                f"""
                <div style="background-color: {entry['color']}; padding: 20px; border-radius: 15px; border-left: 10px solid #333; margin-bottom: 20px; color: #333; min-height: 220px;">
                    <div style="font-size: 1rem; color: #555; margin-bottom: 5px;">{entry['date']}</div>
                    <h3 style="margin-top: 0; margin-bottom: 15px;">{entry['title']}</h3>
                    <div style="display: flex; align-items: flex-start;">
                        <div style="margin-right: 20px;">{archive_canvas}</div>
                        <div style="font-size: 1.1rem; line-height: 1.5;"><b>構成:</b><br>{entry['design']}<br><br><b>メモ:</b><br>{entry['memo']}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
