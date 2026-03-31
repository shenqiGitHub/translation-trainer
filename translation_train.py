# 文件名：translation_train.py

import streamlit as st
import sqlite3
from datetime import datetime
import pandas as pd

# 页面配置与主题样式
st.set_page_config(page_title="回译训练系统", page_icon="📚", layout="wide")
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(180deg, #f8fbff 0%, #f3f7ff 100%);
    }
    h1, h2, h3 {
        letter-spacing: 0.2px;
    }
    .stButton > button {
        border-radius: 10px;
        border: 1px solid #3b82f6;
        background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
        color: white;
        font-weight: 600;
        padding: 0.45rem 1rem;
    }
    .stButton > button:hover {
        border-color: #1d4ed8;
        background: linear-gradient(90deg, #2563eb 0%, #1d4ed8 100%);
    }
    .record-card {
        background: white;
        border: 1px solid #e5e7eb;
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
    }
    .card-title {
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 8px;
    }
    .card-meta {
        color: #64748b;
        font-size: 0.85rem;
        margin-bottom: 10px;
    }
    .card-block {
        padding: 8px 10px;
        border-radius: 10px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        margin-bottom: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 1️⃣ 数据库连接
conn = sqlite3.connect("translation_train.db", check_same_thread=False)
cursor = conn.cursor()

# 2️⃣ 创建表（第一次运行）
cursor.execute('''
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT,
    original TEXT,
    translation TEXT,
    self_eval TEXT,
    doubao_feedback TEXT,
    final_expression TEXT
)
''')
conn.commit()

# 3️⃣ 页面标题
st.title("📚 回译训练系统")
st.caption("记录每次回译练习，快速复盘表达进步轨迹。")

# 4️⃣ 新增记录表单
with st.expander("📝 新增训练记录", expanded=True):
    col_left, col_right = st.columns(2)
    with col_left:
        original = st.text_area("原文", height=120, placeholder="输入待训练原文...")
        translation = st.text_area("回译", height=120, placeholder="输入你的回译结果...")
        self_eval = st.text_area("自评（语法/自然度）", height=100, placeholder="如：语法准确，但语气略生硬。")
    with col_right:
        doubao_feedback = st.text_area("豆包反馈", height=120, placeholder="粘贴外部反馈内容...")
        final_expression = st.text_area("最终表达", height=120, placeholder="整理后最终表达版本...")

    if st.button("保存记录", use_container_width=True):
        if not original.strip() or not translation.strip():
            st.warning("请至少填写“原文”和“回译”后再保存。")
            st.stop()
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute('''
        INSERT INTO records (created_at, original, translation, self_eval, doubao_feedback, final_expression)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (created_at, original, translation, self_eval, doubao_feedback, final_expression))
        conn.commit()
        st.success(f"✅ 记录已保存 ({created_at})")

# 5️⃣ 显示历史记录
st.subheader("📄 历史记录")
df = pd.read_sql_query("SELECT * FROM records ORDER BY created_at DESC", conn)

if df.empty:
    st.info("还没有训练记录，先新增一条开始吧。")
else:
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("总记录数", len(df))
    with m2:
        st.metric("最近记录", df.iloc[0]["created_at"])
    with m3:
        valid_final = df["final_expression"].fillna("").str.strip().astype(bool).sum()
        st.metric("已完成最终表达", int(valid_final))

    tab1, tab2 = st.tabs(["卡片视图", "表格视图"])

    with tab1:
        show_count = st.slider("显示最近记录条数", min_value=1, max_value=min(20, len(df)), value=min(5, len(df)))
        for _, row in df.head(show_count).iterrows():
            st.markdown(
                f"""
                <div class="record-card">
                    <div class="card-title">训练记录 #{row['id']}</div>
                    <div class="card-meta">创建时间：{row['created_at']}</div>
                    <div class="card-block"><b>原文：</b>{row['original'] or ''}</div>
                    <div class="card-block"><b>回译：</b>{row['translation'] or ''}</div>
                    <div class="card-block"><b>自评：</b>{row['self_eval'] or ''}</div>
                    <div class="card-block"><b>豆包反馈：</b>{row['doubao_feedback'] or ''}</div>
                    <div class="card-block"><b>最终表达：</b>{row['final_expression'] or ''}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with tab2:
        keyword = st.text_input("关键词筛选（原文/回译/最终表达）", placeholder="输入关键词后自动筛选...")
        df_view = df.copy()
        if keyword.strip():
            keyword = keyword.strip()
            mask = (
                df_view["original"].fillna("").str.contains(keyword, case=False)
                | df_view["translation"].fillna("").str.contains(keyword, case=False)
                | df_view["final_expression"].fillna("").str.contains(keyword, case=False)
            )
            df_view = df_view[mask]
        st.dataframe(df_view, use_container_width=True, hide_index=True)

# 6️⃣ 导出 CSV
if st.button("导出为 CSV", use_container_width=True):
    df.to_csv("records_export.csv", index=False, encoding='utf-8-sig')
    st.success("✅ 已导出 records_export.csv")