import numpy as np
import pandas as pd
import os

def add_pulse(signal, index, amplitude, fs=40000000):
    """在指定索引处注入一个高频衰减震荡脉冲"""
    pulse_len = 200  # 脉冲持续点数 (200点 @ 40MHz = 5us)
    if index + pulse_len >= len(signal):
        pulse_len = len(signal) - index
    if pulse_len <= 0: return
    
    x = np.arange(pulse_len)
    # 模拟 1MHz 的高频衰减振荡脉冲
    freq_osc = 1000000 
    decay = 20.0
    pulse = amplitude * np.exp(-x / decay) * np.sin(2 * np.pi * (freq_osc / fs) * x)
    signal[index:index+pulse_len] += pulse

def generate_samples():
    print("🚀 正在生成 800,000 点/周期 (40MHz, 50Hz) 的高清局放波形...")
    
    fs = 40000000  # 40MHz 采样率
    freq = 50      # 50Hz 工频
    points = int(fs / freq) # 800,000 点
    
    # 生成纯净的 20A 基波电流
    t = np.linspace(0, 1/freq, points, endpoint=False)
    base_current = 20.0 * np.sin(2 * np.pi * freq * t)
    
    # ==========================================
    # 1. 🟡 悬浮电位放电 (Floating Potential)
    # 专家阈值: 密度 > 100, 不对称度 < 0.2
    # 物理特征: 极度密集，相位广泛，幅值削顶 (平齐)
    # ==========================================
    print("⏳ 生成 [悬浮电位] 样本...")
    sig_floating = base_current.copy() + np.random.randn(points) * 0.05
    # 生成 400 个脉冲，广泛分布在整个周期
    indices_floating = np.random.randint(0, points, size=400)
    for idx in indices_floating:
        # 强制削顶特征：幅值全部锁定在绝对值 5.0 左右
        sign = 1 if idx < points // 2 else -1 # 保证正负半周对称
        add_pulse(sig_floating, idx, sign * (5.0 + np.random.uniform(-0.1, 0.1)), fs)
    
    pd.DataFrame({'Phase_A': sig_floating}).to_csv('sample_floating_potential.csv', index=False)


    # ==========================================
    # 2. 🟡 变频器/开关噪声 (VFD / Switching)
    # 专家阈值: 密度 < 50, 聚集在 120° 或 240°
    # 物理特征: 死锁在固定的换相角度
    # ==========================================
    print("⏳ 生成 [变频器噪声] 样本...")
    sig_vfd = base_current.copy() + np.random.randn(points) * 0.05
    # 在 120° (points/3) 和 240° (points*2/3) 注入共 40 个高能脉冲
    idx_120 = points // 3
    idx_240 = points * 2 // 3
    for _ in range(25):
        add_pulse(sig_vfd, idx_120 + np.random.randint(-1000, 1000), np.random.uniform(6.0, 9.0), fs)
    for _ in range(15):
        add_pulse(sig_vfd, idx_240 + np.random.randint(-1000, 1000), np.random.uniform(-9.0, -6.0), fs)
        
    pd.DataFrame({'Phase_A': sig_vfd}).to_csv('sample_vfd_noise.csv', index=False)


    # ==========================================
    # 3. 🔵 空间电晕/白噪声 (Corona / White Noise)
    # 专家阈值: 密度 > 50, 且不满足其它规则 (自带一定随机性)
    # 物理特征: 随电压峰值(90°/270°)出现，高度随机
    # ==========================================
    print("⏳ 生成 [空间电晕] 样本...")
    # 电晕带有更高的背景白噪
    sig_corona = base_current.copy() + np.random.randn(points) * 0.2 
    idx_90 = points // 4
    idx_270 = points * 3 // 4
    
    # 正半周 100 个，负半周 50 个，制造 0.33 的不对称度 (避开悬浮和沿面污闪的判定区)
    for _ in range(100):
        # 散布在 90 度周围
        idx = int(np.random.normal(idx_90, points // 20))
        if 0 <= idx < points:
            add_pulse(sig_corona, idx, np.random.uniform(2.0, 7.0), fs)
            
    for _ in range(50):
        # 散布在 270 度周围
        idx = int(np.random.normal(idx_270, points // 20))
        if 0 <= idx < points:
            add_pulse(sig_corona, idx, np.random.uniform(-7.0, -2.0), fs)

    pd.DataFrame({'Phase_A': sig_corona}).to_csv('sample_corona_noise.csv', index=False)

    print("✅ 全部生成完毕！文件已保存在当前目录:")
    print("   - sample_floating_potential.csv")
    print("   - sample_vfd_noise.csv")
    print("   - sample_corona_noise.csv")

if __name__ == "__main__":
    generate_samples()
