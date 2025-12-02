import streamlit as st
from openai import OpenAI

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="AI 学术润色 Pro",
    page_icon="🎓",
    layout="wide"
)

# --- 2. 初始化 Session State (记忆库) ---
# 这是为了让 AI 记住上一轮生成的内容，不会一刷新就没了
if "output_text" not in st.session_state:
    st.session_state.output_text = ""

# --- 3. 侧边栏配置 ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2014/2014350.png", width=60)
    st.title("⚙️ 控制面板")

    api_key = st.text_input("🔑 API Key", type="password", help="输入 DeepSeek Key")
    base_url = "https://api.deepseek.com"

    st.markdown("---")

    st.subheader("🎨 风格选择")
    style_option = st.selectbox(
        "选择目标语言风格",
        ("地道学术 (Academic)", "简洁明了 (Concise)", "原生口语 (Native)", "复杂的长难句 (Complex)"),
        index=0
    )

    # 新增：清空按钮
    if st.button("🗑️ 清空所有内容", type="secondary"):
        st.session_state.output_text = ""
        st.rerun()  # 强制刷新页面

    st.markdown("---")
    st.info(
        "📖 **使用指南**：\n1. 配置 Key 并输入原文。\n2. 点击运行，等待流式输出。\n3. 生成结束后，点击右上角 **复制图标** 即可。")

# --- 4. 主界面 ---
st.title("🎓 学术论文润色助手 Pro")
st.caption(f"当前模式：**{style_option}** | 智能记忆已开启 🧠")

col1, col2 = st.columns([1, 1])

# --- 左侧：输入区 ---
with col1:
    st.subheader("📝 原文输入")
    user_input = st.text_area(
        "在此粘贴中文或初稿英文",
        height=400,
        placeholder="例如：The method uses deep learning to solve..."
    )

# --- 右侧：输出区 (逻辑升级) ---
with col2:
    st.subheader("✨ 润色结果")

    # 创建一个空的容器，用于动态显示内容
    output_container = st.container(border=True, height=400)

    # 如果 Session State 里有存货，先显示存货
    if st.session_state.output_text:
        with output_container:
            # 【关键修改】：这里改回 text_area
            # 1. height=None 代表自动填满容器的高度
            # 2. label_visibility="collapsed" 隐藏掉上面的小标题，更清爽
            st.text_area(
                label="Result",
                value=st.session_state.output_text,
                height=480,  # 稍微留点余地给 padding
                label_visibility="collapsed"
            )

            # 在文本框下面加一个小提示，弥补没有复制按钮的遗憾
            st.caption(f"📝 字数统计: {len(st.session_state.output_text)} 字符 | Tip: 点击框内 Ctrl+A 可全选复制")

# --- 5. 按钮逻辑区 ---
# 放在外面，让布局更协调
st.markdown("---")
btn_col1, btn_col2, btn_col3 = st.columns([1, 2, 1])

with btn_col2:
    # 动态改变按钮文字：如果已经有内容了，就显示“重新生成”
    btn_label = "🔄 重新生成 (Regenerate)" if st.session_state.output_text else "🚀 开始润色 (Run)"
    submit_btn = st.button(btn_label, use_container_width=True, type="primary")

# --- 6. 核心处理逻辑 ---
if submit_btn:
    if not api_key:
        st.toast("⚠️ 记得填写 API Key 哦！")
        st.stop()
    if not user_input:
        st.toast("⚠️ 原文不能为空！")
        st.stop()

    client = OpenAI(api_key=api_key, base_url=base_url)

    system_prompt = f"你是一位资深的顶级期刊审稿人。请将用户的输入重写为【{style_option}】风格的英文。保持原意，修复语法错误，提升词汇高级感。直接输出内容，不要任何寒暄。"

    try:
        # 清空容器，准备接收新的流
        output_container.empty()

        with output_container:
            # 1. 占位符提示
            status_text = st.empty()
            status_text.markdown("Wait a moment... AI 正在思考中 🧠")

            # 2. 发起流式请求
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                stream=True
            )

            # 3. 核心：write_stream 会实时打印，并返回最终完整的字符串
            generated_text = st.write_stream(stream)

            # 4. 只有生成完了，才清空上面的“思考中”提示
            status_text.empty()

            # 5. 【关键】把结果存入 Session State
            st.session_state.output_text = generated_text

            # 6. 强制刷新一下，为了让 st.code (带复制按钮的那种) 替换掉刚才的流式文本
            # 这一步是为了让界面变成“可复制状态”
            st.rerun()

    except Exception as e:
        st.error(f"出错了: {e}")

# --- 7. 底部版权 ---
st.markdown(
    """
    <div style='text-align: center; color: #888; font-size: 12px; margin-top: 20px;'>
        🛠️ 由乳酸菌水乐开发 | 📚 仅供学术交流 | 🚫 严禁用于商业用途 <br>
        <i>Powered by DeepSeek & Streamlit</i>
    </div>
    """,
    unsafe_allow_html=True
)