import math
import numpy as np
import iric
import sys
import os

print("----------Start----------")

###############################################################################
# CGNSを開く
###############################################################################

# iRICで動かす時用
# =============================================================================
if len(sys.argv) < 2:
    print("Error: CGNS file name not specified.")
    exit()

cgns_name = sys.argv[1]

print("CGNS file name: " + cgns_name)

# CGNSをオープン
fid = iric.cg_iRIC_Open(cgns_name, iric.IRIC_MODE_MODIFY)

# コマンドラインで動かす時用
# =============================================================================

# CGNSをオープン
# fid = iric.cg_iRIC_Open("E:/hoshino/project/debug/debug_solver_1d/Case1.cgn", iric.IRIC_MODE_MODIFY)

# 分割保存したい場合はこれを有効にする
# os.environ['IRIC_SEPARATE_OUTPUT'] = '1'

###############################################################################
# 古い計算結果を削除
###############################################################################

iric.cg_iRIC_Clear_Sol(fid)

###############################################################################
# 計算条件を読み込み
###############################################################################

length = iric.cg_iRIC_Read_Real(fid,"length")
grid_interval = iric.cg_iRIC_Read_Real(fid,"grid_interval")

# 格子サイズを読み込み
isize = int(length/grid_interval)+1

grid_x_arr = np.arange(isize, dtype=np.float32) * grid_interval

# 計算時間を読み込み
time_end = iric.cg_iRIC_Read_Integer(fid, "time_end")

# 読み込んだ格子サイズをコンソールに出力
print("Grid size:")
print("    isize= " + str(isize))

###############################################################################
# 格子書き込み
###############################################################################

iric.cg_iRIC_Write_Grid1d_Coords(fid,isize,grid_x_arr)

###############################################################################
# メモリ確保
###############################################################################

elevation = np.arange(isize, dtype=np.float32) ** 2
water_level = np.zeros(shape=(isize), order="F", dtype=np.float32)

iric.cg_iRIC_Write_Grid_Real_Node(fid,"elevation",elevation)
iric.cg_iRIC_Write_Grid_Real_Node(fid,"water_level",water_level)

print("----------mainloop start----------")

###############################################################################
# メインループスタート
###############################################################################

for t in range(time_end + 1):

    water_level[:] = float(isize) ** 2*(t/time_end)

    ###########################################################################
    # 結果の書き込みスタート
    ###########################################################################

    # 時間ごとの書き込み開始をGUIに伝える
    iric.cg_iRIC_Write_Sol_Start(fid)

    # 時刻を書き込み
    iric.cg_iRIC_Write_Sol_Time(fid, float(t))

    iric.cg_iRIC_Write_Sol_BaseIterative_Real(fid,"discharge",float(t))

    iric.cg_iRIC_Write_Sol_Node_Real(fid,"elevation",elevation)
    iric.cg_iRIC_Write_Sol_Node_Real(fid,"water_level",water_level)

    # CGNSへの書き込み終了をGUIに伝える
    iric.cg_iRIC_Write_Sol_End(fid)

    # コンソールに時間を出力
    print("t= " + str(t))

    # 計算結果の再読み込みが要求されていれば出力を行う
    iric.cg_iRIC_Check_Update(fid)

    # 計算のキャンセルが押されていればループを抜け出して出力を終了する。
    canceled = iric.iRIC_Check_Cancel()
    if canceled == 1:
        print("Cancel button was pressed. Calculation is finishing. . .")
        break

print("----------finish----------")

###############################################################################
# 計算終了処理
###############################################################################
iric.cg_iRIC_Close(fid)

###############################################################################
# 計算結果を壊す処理（デバッグ用）
###############################################################################

# Case1を破壊
# fname = 'Case1.cgn'
# with open(fname, 'w') as f:
#     f.write('BROKEN')

# 分割する場合
# fname = 'result/Solution' + str(time_end + 1) + '.cgn'
# with open(fname, 'w') as f:
#     f.write('BROKEN')
