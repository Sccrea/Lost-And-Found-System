import serial
import time
import crcmod

# 创建CRC16校验函数 (Modbus RTU模式)
crc16 = crcmod.mkCrcFun(0x18005, rev=True, initCrc=0xFFFF)

def control_lock(serial_port, device_addr, lock_num, action, duration=5):
    """
    控制电锁
    :param serial_port: 串口对象
    :param device_addr: 锁控板地址 (1-255)
    :param lock_num: 锁路号 (0-7)
    :param action: 0=关锁, 1=开锁
    :param duration: 开锁时长(秒)
    """
    # 构建指令 (功能码05)
    cmd = bytearray([
        device_addr,    # 设备地址
        0x05,           # 功能码（单路控制）
        0x00,           # 寄存器地址高字节
        lock_num,       # 寄存器地址低字节（锁路号）
        (0xFF if action==1 else 0x00),  # 开锁
        0x00            # 固定0
    ])
    
    # 添加持续时间（可选）
    if duration > 0:
        cmd.extend([duration >> 8, duration & 0xFF])
    
    # 计算CRC16校验码
    crc = crc16(cmd)
    cmd.append(crc & 0xFF)        # CRC低字节
    cmd.append((crc >> 8) & 0xFF) # CRC高字节
    
    # 发送指令
    serial_port.write(cmd)
    print(f"发送指令: {cmd.hex(' ')}")
    
    # 读取响应 (等待100ms)
    time.sleep(0.1)
    response = serial_port.read_all()
    if response:
        print(f"收到响应: {response.hex(' ')}")

# 主程序
def open_lock(lock_number):
    num=lock_number
    if __name__ == "__main__":
        # 配置串口 (根据实际设备修改)
        ser = serial.Serial(
            port='/dev/ttyUSB0',   # USB转485设备
            baudrate=9600,          # 常见波特率
            bytesize=8,
            parity='N',
            stopbits=1,
            timeout=0.5
        )
    
        try:
        #控制地址01的设备，第1路开锁
            control_lock(ser, 0x00, num, 1)
            
            # 控制地址02的设备，第4路关锁
            # control_lock(ser, 0x02, 0x03, 0)
        
        except Exception as e:
            print(f"错误: {str(e)}")
        finally:
            ser.close()
    print(num)
