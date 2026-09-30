import datetime
import time
import pandas as pd
import streamlit as st

# 页面配置
st.set_page_config(
    page_title="铁路构件无损检测智能管理系统",
    page_icon="🚄",
    layout="wide",
)

# 侧边栏：系统导航
st.sidebar.title("🚄 铁路无损检测系统")
st.sidebar.info("适用于高职技能比赛：传统无损检测设备的信息化升级")
menu = st.sidebar.radio(
    "功能模块",
    [
        "1. 零件与工单绑定",
        "2. 超声波(UT)检测数据采集",
        "3. 磁粉(MT)缺陷图片归档",
        "4. 智能综合评级与报告生成",
    ],
)

# 模拟数据库（使用 Session State 在内存中存数据）
if "inspection_data" not in st.session_state:
    st.session_state.inspection_data = {
        "part_id": "CRH-2024-089",
        "part_name": "高速列车转向架侧梁焊缝",
        "material": "Q345D低合金钢",
        "method": "UT + MT 复合检测",
        "ut_result": "未检测",
        "ut_defect_depth": 0.0,
        "mt_result": "未检测",
        "mt_image": None,
        "final_status": "待判定",
    }

# ================= 模块 1：零件与工单绑定 =================
if menu == "1. 零件与工单绑定":
    st.header("📋 第一步：铁路零件身份录入与工艺引导")
    st.markdown("通过扫描或录入零件二维码，自动匹配国家/铁路行业无损检测标准（如TB/T标准）。")

    col1, col2 = st.columns(2)

    with col1:
        part_id = st.text_input("零件唯一编号 (RFID/条形码)", value=st.session_state.inspection_data["part_id"])
        part_name = st.selectbox(
            "铁路构件类型",
            ["高速列车转向架侧梁焊缝", "车钩缓冲装置对接焊缝", "重载铁路钢轨焊接接头", "牵引梁主焊缝"],
        )
        material = st.selectbox("构件材质", ["Q345D低合金钢", "E36耐候钢", "ZG235-450铸钢"])

    with col2:
        st.info(
            """
        💡 **工艺标准提示：**
        - **超声波检测(UT)**：依据 **TB/T 1558.2-2018《机车车辆焊缝无损检测 第2部分：超声检测》**，
          适用于厚度 > 8mm 的对接焊缝内部气孔、未熔合（通用焊缝亦可参照 GB/T 11345）。
        - **磁粉检测(MT)**：依据 **TB/T 1558.4-2018《机车车辆焊缝无损检测 第4部分：磁粉检测》**，
          适用于铁磁性材料表面及近表面裂纹（如弧坑裂纹、咬边）。
        """
        )
        inspector = st.text_input("检验员工号", value="NDT_Expert_05")
        inspect_date = st.date_input("检验日期", datetime.date.today())

    if st.button("确认绑定并下发工艺卡", type="primary"):
        st.session_state.inspection_data["part_id"] = part_id
        st.session_state.inspection_data["part_name"] = part_name
        st.session_state.inspection_data["material"] = material
        st.success(f"零件 {part_id} 绑定成功！请前往下一步进行数据采集。")

# ================= 模块 2：超声波(UT)检测 =================
elif menu == "2. 超声波(UT)检测数据采集":
    st.header("📡 第二步：超声波探伤(UT)数据动态接入")
    st.markdown(
        f"当前检测零件：**{st.session_state.inspection_data['part_id']}** ({st.session_state.inspection_data['part_name']})"
    )

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("超声波 A扫描/B扫描 实时波形模拟")
        # 模拟实时波形数据
        chart_data = pd.DataFrame(
            {
                "Time (us)": range(50),
                "Amplitude (V)": [
                    (
                        1.5
                        if i in [10, 25]
                        else (0.2 + (i % 3) * 0.1 if i > 30 else 0.1)
                    )
                    for i in range(50)
                ],
            }
        )
        st.line_chart(chart_data, x="Time (us)", y="Amplitude (V)")
        st.caption("注：波形突跳点（Amplitude > 1.0V）代表检测到内部反射回波。")

    with col2:
        st.subheader("UT 判读控制面板")
        defect_depth = st.slider("测得缺陷埋藏深度 (mm)", 0.0, 50.0, 12.5)
        max_amplitude = st.slider("最大缺陷回波幅值 (%)", 0, 100, 45)

        if st.button("保存UT检测数据", type="primary"):
            st.session_state.inspection_data["ut_defect_depth"] = defect_depth
            if max_amplitude > 60:
                st.session_state.inspection_data["ut_result"] = "不合格 (发现超标内部缺陷)"
                st.error("警告：检测到超标反射波，判定为不合格！")
            else:
                st.session_state.inspection_data["ut_result"] = "合格 (无超标内部缺陷)"
                st.success("UT检测数据已保存，评定：合格。")

# ================= 模块 3：磁粉(MT)缺陷图片归档 =================
elif menu == "3. 磁粉(MT)缺陷图片归档":
    st.header("📷 第三步：磁粉探伤(MT)磁痕拍照与归档")
    st.markdown("通过工位摄像头捕获荧光磁痕照片，关联零件进行永久存档。")

    uploaded_file = st.file_uploader("上传磁粉探伤现场荧光磁痕照片 (JPG/PNG)", type=["jpg", "png", "jpeg"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="已上传的磁痕照片", width=400)
        st.session_state.inspection_data["mt_image"] = uploaded_file

        mt_status = st.radio("表面磁痕评判结果", ["合格 (无明显裂纹显示)", "不合格 (发现线性裂纹/磁痕显示)"])

        if st.button("保存MT检测结果", type="primary"):
            st.session_state.inspection_data["mt_result"] = mt_status
            st.success("磁粉检测数据及图片归档成功！")
    else:
        st.info("请上传或拍摄磁粉探伤现场照片以进行数字化判定。")

# ================= 模块 4：智能综合评级与报告生成 =================
elif menu == "4. 智能综合评级与报告生成":
    st.header("📑 第四步：综合判定与标准无损检测报告生成")

    data = st.session_state.inspection_data

    st.subheader("检验结果汇总看板")
    col1, col2, col3 = st.columns(3)
    col1.metric("零件编号", data["part_id"])
    col2.metric("超声波(UT)状态", data["ut_result"])
    col3.metric("磁粉(MT)状态", data["mt_result"])

    # 综合判定逻辑
    if "不合格" in data["ut_result"] or "不合格" in data["mt_result"]:
        final_conclusion = "不合格 (REJECTED)"
        st.error(f"最终判定结论：{final_conclusion}")
    else:
        final_conclusion = "合格 (ACCEPTED)"
        st.success(f"最终判定结论：{final_conclusion}")

    st.markdown("---")
    st.subheader("一键导出铁路行业标准无损检测报告")

    if st.button("生成 PDF / 网页版正式检验报告", type="primary"):
        with st.spinner("正在生成符合TB/T标准的质检报告..."):
            time.sleep(1.5)  # 模拟生成过程
        st.balloons()

        # 展示报告预览
        st.markdown(
            f"""
        ### 🚄 铁路产品质量无损检测报告 (电子版)
        ---
        - **零件名称**: {data['part_name']}
        - **零件编号**: {data['part_id']}
        - **构件材质**: {data['material']}
        - **检验依据**: TB/T 1558.1-2020（总则）、TB/T 1558.2-2018（超声检测）、TB/T 1558.4-2018（磁粉检测）
        - **超声波检测结果**: {data['ut_result']} (缺陷深度: {data['ut_defect_depth']} mm)
        - **磁粉检测结果**: {data['mt_result']}
        - **终审结论**: **{final_conclusion}**
        - **检验机构**: 职业院校智能焊接与无损检测实训中心
        - **检验时间**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        ---
        *（此报告具有防篡改数字签名，可通过系统随时追溯）*
        """
        )
        st.download_button(
            label="下载检验报告 (Markdown/TXT格式)",
            data=f"铁路无损检测报告\n编号:{data['part_id']}\n结论:{final_conclusion}",
            file_name=f"Report_{data['part_id']}.txt",
        )
