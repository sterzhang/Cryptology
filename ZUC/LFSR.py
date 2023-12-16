state = 0b1101  
first_state = 0b1101

def lfsr_step_1(state):
    # 计算反馈位
    feedback = ((state >> 3) ^ (state >> 0)) & 1
    # 右移寄存器并把反馈放到高位上
    state = (feedback << 3) | (state >> 1)
    # 确保寄存器仍然是4位
    return state & 0b1111 


def lfsr_step_2(state):
    # 计算反馈位
    feedback = ((state >> 3) ^ (state >> 2)) & 1
    # 右移寄存器并把反馈放到高位上
    state = (feedback << 3) | (state >> 1)
    # 确保寄存器仍然是4位
    return state & 0b1111  


print("使用本原多项式 g1(x)=x^4 + x + 1 为连接多项式组成线性移位寄存器：")
print(f'{first_state:04b}')
for i in range(20):
    state = lfsr_step_1(state)
    if state == first_state and i > 0:
        print(f"周期为{i+1}")
        break 
    print(f'{state:04b}') 

print("使用本原多项式 g2(x) = x^4 + x^3 + 1 为连接多项式组成线性移位寄存器")
print(f'{first_state:04b}')
for i in range(20):
    state = lfsr_step_2(state)
    if state == first_state and i > 0:
        print(f"周期为{i+1}")
        break
    print(f'{state:04b}')  





# def lfsr_step_1(state):
#     feedback = ((state >> 3) ^ (state >> 0)) & 1
#     state = (feedback << 3) | (state >> 1)
#     return state & 0b1111 

# def lfsr_step_2(state):
#     feedback = ((state >> 3) ^ (state >> 2)) & 1
#     state = (feedback << 3) | (state >> 1)
#     return state & 0b1111

# def find_optimal_state():
#     max_period = 15  # 最大周期长度

#     for initial_state in range(1, 16):  # 遍历所有非零初始状态
#         state_1 = initial_state
#         state_2 = initial_state

#         for i in range(max_period):
#             state_1 = lfsr_step_1(state_1)
#             state_2 = lfsr_step_2(state_2)

#             # 如果两个LFSR都回到了初始状态，且周期等于最大周期
#             if state_1 == initial_state and state_2 == initial_state and i == max_period - 1:
#                 return initial_state  # 找到最佳初始状态

#     return None  # 如果没有找到，返回None

# optimal_state = find_optimal_state()
# if optimal_state is not None:
#     print(f"找到最佳初始状态: {optimal_state:04b}")
# else:
#     print("没有找到能使两个LFSR都达到最大周期的初始状态")
