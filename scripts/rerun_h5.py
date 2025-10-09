import os
import rerun as rr
import h5py
import numpy as np
DIR_PATH = os.path.dirname(os.path.abspath(__file__))

h5_path = DIR_PATH + "/episode_0.h5"
camera_names = ["in_hand", "up", "front"]

rr.init("Episode Replay", spawn=True)

with h5py.File(h5_path, "r") as f:
    N, D = f["action"].shape
    for i in range(N):
        rr.set_time_sequence("frame", i)

        for cam in camera_names:
            rgb = f[f"{cam}/rgb"][i]
            depth = f[f"{cam}/depth"][i]

            rr.log(f"{cam}/rgb", rr.Image(rgb))
            rr.log(f"{cam}/depth", rr.DepthImage(depth))

        for j in range(D):
            rr.log(f"joints/scalar/joint{j}", rr.Scalars(f["action"][i][j]))

        rr.log("joints/vector", rr.Tensor(f["action"][i]))
