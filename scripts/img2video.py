import os
import h5py
import imageio
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
# print(f"DIRPATH: {DIRPATH}")
# exit()

# cam_name = "in_hand"
cam_name = "up"
# cam_name = "front"
h5_path = DIR_PATH + "/episode_0.h5"
video_path = DIR_PATH + f"/episode_0_{cam_name}.mp4"

fps = 20

with h5py.File(h5_path, "r") as f:
    rgb_data = f[f"{cam_name}/rgb"][:]  # 一次性读到内存 (N,H,W,3)

imageio.mimsave(video_path, rgb_data, fps=fps)
print(f"✅ 视频保存完成: {video_path}")
