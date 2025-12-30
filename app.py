import streamlit as st
import re
from pypinyin import pinyin, Style
import PyPDF2
from io import StringIO

# ==========================================
# 1. 页面配置与科幻风格 CSS 设计
# ==========================================
st.set_page_config(
    page_title="IPA & Pinyin Converter | 智能语音转换终端",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 科幻/赛博朋克风格 CSS (保持之前的高清修复)
sci_fi_css = """
<style>
    /* 顶部条背景色 */
    header[data-testid="stHeader"] {
        background-color: #0e1117 !important;
    }

    /* 全局背景 */
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
        font-family: 'Roboto Mono', 'Courier New', monospace;
    }
    
    /* 主标题样式 */
    .main-title {
        color: #00f2ea;
        text-shadow: 0 0 10px rgba(0, 242, 234, 0.6);
        font-weight: 700;
        letter-spacing: 2px;
        margin-bottom: 20px;
    }

    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #00f2ea !important;
        text-shadow: none !important;
        font-weight: 800 !important;
    }
    
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] div[role="radiogroup"],
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
        text-shadow: none !important;
        font-weight: 500 !important;
    }

    /* 输入框样式 */
    .stTextArea textarea, .stTextInput input {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        color: #00f2ea !important;
        border-radius: 4px;
        caret-color: #00f2ea;
    }
    
    /* 占位符/提示文字 (Placeholder) 高亮修复 */
    ::placeholder { 
        color: #a0aabf !important;
        opacity: 1 !important;
    }
    ::-moz-placeholder {
        color: #a0aabf !important;
        opacity: 1 !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #00f2ea !important;
        box-shadow: 0 0 8px rgba(0, 242, 234, 0.5);
    }
    
    /* 只读状态 (Disabled) 高亮修复 */
    .stTextArea textarea:disabled, .stTextInput input:disabled {
        color: #00f2ea !important;
        -webkit-text-fill-color: #00f2ea !important;
        opacity: 1 !important;
        background-color: #121418 !important; 
        border: 1px dashed #40464d !important;
        cursor: not-allowed;
    }

    /* Tabs 样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #161b22;
        border-radius: 4px;
        border: 1px solid #30363d;
    }
    .stTabs [data-baseweb="tab"] p {
        color: #a0aabf !important;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #21262d !important;
        border: 1px solid #00f2ea !important;
    }
    .stTabs [aria-selected="true"] p {
        color: #00f2ea !important;
    }

    /* 按钮样式 */
    .stButton>button {
        background: linear-gradient(45deg, #007bff, #00f2ea);
        color: #000;
        font-weight: bold;
        border: none;
        border-radius: 4px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        width: 100%;
    }
    .stButton>button:hover {
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(0, 242, 234, 0.6);
    }
    
    /* 底部版权 */
    .footer {
        margin-top: 50px;
        padding-top: 20px;
        border-top: 1px solid #30363d;
        text-align: center;
        color: #8b949e;
        font-size: 0.8em;
    }
    .footer span {
        color: #00f2ea;
    }
</style>
"""
st.markdown(sci_fi_css, unsafe_allow_html=True)

# ==========================================
# 2. 核心逻辑函数
# ==========================================
# (保持逻辑不变)
base_pinyin_to_ipa = {
    'zh': 'ʈʂ', 'ch': 'ʈʂʰ', 'sh': 'ʂ', 'r': 'ʐ','z': 'ts', 'c': 'tsʰ', 's': 's','g':'k','k':'kʰ','h':'x',
    'd':'t','t':'tʰ','n':'n','l':'l','b':'p','p':'pʰ','m':'m','f':'f','j':'tɕ','q':'tɕʰ','x':'ɕ','ng':'ŋ',
    'zi':'tsɿ','ci':'tsʰɿ','si':'sɿ','zhi':'ʈʂʅ','chi':'ʈʂʰʅ','shi':'ʂʅ','ri':'ʐʅ',
    'y': 'i', 'ü': 'y', 'u': 'u', 'i': 'i', 'o': 'o', 'ê': 'ɛ', 'e': 'ɤ', 'a': 'A', 'ian': 'iɛn', 'üan': 'yɛn',
    'ie': 'iɛ','üe':'yɛ','er':'ɚ','ia':'iA','ua':'uA','uo':'uo', 'en': 'ən','ai':'ai','uai':'uai','ei':'ei','uei':'uei',
    'ao': 'ɑu','iao':'iɑu','ou':'ou','iou':'iou','an':'an','uan':'uan','en':'ən', 'uen':'uən',
    'in':'in','ün':'yn','ang': 'ɑŋ','iang': 'iɑŋ','uang':'uɑŋ',
    'eng':'ɤŋ','ing':'iŋ','ueng':'uɤŋ','ong':'uŋ','iong':'yŋ','yong':'yŋ',
    'yi':'i','wu':'u','yu':'y', 'yue':'yɛ','weng':'uɤŋ',
    'jue':'tɕyɛ','que':'tɕʰyɛ','xue':'ɕyɛ','ju':'tɕy','qu':'tɕʰy','xu':'ɕy','juan':'tɕyɛn','quan':'tɕʰyɛn','xuan':'ɕyɛn',
    'jun':'tɕyn','qun':'tɕʰyn','xun':'ɕyn','jiong':'tɕyŋ','qiong':'tɕʰyŋ','xiong':'ɕyŋ',
    'yuan':'yɛn','juan':'tɕyɛn','quan':'tɕʰyɛn','xuan':'ɕyɛn',
    'wei':'uei','ye':'iɛ','xu':'ɕy','wo':'uo','you':'iou','wei':'uei','wen':'uən','ui':'uei','un':'uən','iu':'iou',
    '。':'.'
}

tone_map = {
    '1': '⁵⁵', '2': '³⁵', '3': '²¹⁴', '4': '⁵¹', '0': '' 
}

def get_ipa_dict(with_tone=False):
    mapping = base_pinyin_to_ipa.copy()
    if with_tone:
        mapping.update(tone_map)
    else:
        for k in tone_map.keys():
            mapping[k] = ''
    return mapping

def pinyin_to_ipa_convert(text_segment, with_tone=False):
    current_map = get_ipa_dict(with_tone)
    pattern = '|'.join(sorted(current_map.keys(), key=len, reverse=True)) + '|.'
    syllables = re.findall(pattern, text_segment)
    word_ipa = ''
    for syllable in syllables:
        word_ipa += current_map.get(syllable, syllable)
    return word_ipa

def core_converter(text, target_mode, tone_mode):
    if not text:
        return ""
    lines = text.split('\n')
    result_lines = []
    for line in lines:
        line = line.strip()
        if not line:
            result_lines.append("")
            continue
        if target_mode == '汉语拼音 (Pinyin)':
            style = Style.TONE if tone_mode == '带声调' else Style.NORMAL
            pinyin_list = pinyin(line, style=style, heteronym=False)
            line_result = ' '.join([item[0] for item in pinyin_list])
            result_lines.append(line_result)
        else:
            pinyin_list = pinyin(line, style=Style.TONE3, heteronym=False)
            pinyin_str = ' '.join([item[0] for item in pinyin_list])
            original_numbers = re.findall(r'\d+', line)
            temp_pinyin_str = re.sub(r'(\d)', r'|\1|', pinyin_str) 
            is_tone_needed = (tone_mode == '带声调')
            ipa_sentence = pinyin_to_ipa_convert(temp_pinyin_str, with_tone=is_tone_needed)
            for num in set(original_numbers):
                ipa_sentence = ipa_sentence.replace(f'|{num}|', num)
            ipa_sentence = ipa_sentence.replace("|", "")
            result_lines.append(ipa_sentence)
    return '\n'.join(result_lines)

def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    text = ""
    for page in pdf_reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text

# ==========================================
# 3. 页面布局与交互逻辑 (精简版)
# ==========================================

# --- 侧边栏 ---
with st.sidebar:
    st.title("🎛️ 控制面板")
    st.markdown("---")
    
    st.subheader("输出格式")
    target_format = st.radio(
        "选择转换目标：",
        ('国际音标 (IPA)', '汉语拼音 (Pinyin)'),
        index=0
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.subheader("声调设置")
    tone_option = st.radio(
        "声调模式：",
        ('带声调', '不带声调'),
        index=0
    )
    
    st.markdown("---")
    st.info("💡 提示：IPA 模式下使用了五度标记法（如 ⁵⁵）来表示声调。")

# --- 主界面 ---
st.markdown('<h2 class="main-title">⚡ 国际音标 / 拼音生成小工具</h2>', unsafe_allow_html=True)

# Tab 布局
tab1, tab2 = st.tabs(["📝 直接输入文本", "📂 上传文件转换"])

# --- Tab 1: 文本输入 ---
with tab1:
    # [修改] 移除了 "#### 输入内容的标签及文本框"
    # [修改] 隐藏了 label，让界面更干净
    user_input = st.text_area(
        label="Input Text", # 为了无障碍访问保留标签内容，但视觉上隐藏
        label_visibility="collapsed", 
        height=150, 
        placeholder="在此输入需要转换的中文文本... (支持多行)"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        start_convert_btn = st.button("🚀 开始转换", key="btn_text")

    if start_convert_btn and user_input:
        with st.spinner('正在进行量子解析...'):
            result_text = core_converter(user_input, target_format, tone_option)
            st.success("转换完成")
            # [修改] 移除了 "#### 显示结果的标签及文本框"
            st.code(result_text, language=None)

# --- Tab 2: 文件上传 ---
with tab2:
    # [修改] 移除了 "#### 上传文件..."
    # [修改] 隐藏了 label
    uploaded_file = st.file_uploader(
        label="Upload File",
        label_visibility="collapsed",
        type=['txt', 'pdf']
    )
    
    file_content = ""
    
    if uploaded_file is not None:
        if uploaded_file.type == "text/plain":
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            file_content = stringio.read()
        elif uploaded_file.type == "application/pdf":
            file_content = read_pdf(uploaded_file)
            
        # [修改] 移除了 "#### 预览文件内容"
        st.text_area(
            label="File Preview",
            label_visibility="collapsed",
            value=file_content[:1000] + ("..." if len(file_content)>1000 else ""), 
            height=200, 
            disabled=True 
        )
        
        col_f1, col_f2, col_f3 = st.columns([1, 2, 1])
        with col_f2:
            start_file_convert_btn = st.button("🚀 开始转换文件", key="btn_file")
            
        if start_file_convert_btn and file_content:
            with st.spinner('正在处理数据流...'):
                converted_result = core_converter(file_content, target_format, tone_option)
                # [修改] 移除了 "#### 显示结果及下载"
                st.text_area(
                    label="Result Preview",
                    label_visibility="collapsed",
                    value=converted_result, 
                    height=200
                )
                
                out_name = f"converted_{uploaded_file.name.split('.')[0]}.txt"
                st.download_button(
                    label="💾 下载转换结果 (.txt)",
                    data=converted_result,
                    file_name=out_name,
                    mime="text/plain"
                )

# ==========================================
# 4. 底部版权信息
# ==========================================
st.markdown(
    """
    <div class="footer">
        本软件由华中师范大学 <span>沈威</span> 制作 | 联系邮箱：<span>sw@ccnu.edu.cn</span>
    </div>
    """,
    unsafe_allow_html=True
)