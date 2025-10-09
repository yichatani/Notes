import os
import h5py
import pandas as pd
import cv2
import io
DIR_PATH = os.path.dirname(os.path.abspath(__file__))

h5_path = DIR_PATH + "/episode_0.h5"
parquet_path = DIR_PATH + "/episode_0.parquet"

# cam_name = "in_hand"
cam_name = "up"
# cam_name = "front"

rows = []
with h5py.File(h5_path, "r") as f:
    N = f["action"].shape[0]
    for i in range(N):
        row = {
            "index": int(f["index"][i]),
            "action": f["action"][i].tolist(),
            "agent_pos": f["agent_pos"][i].tolist(),
        }

        rgb = f["cam1/rgb"][i]
        depth = f["cam1/depth"][i]

        _, rgb_bytes = cv2.imencode(".png", rgb)
        _, depth_bytes = cv2.imencode(".png", depth.astype("uint16"))

        row["cam1_rgb"] = rgb_bytes.tobytes()
        row["cam1_depth"] = depth_bytes.tobytes()

        rows.append(row)

df = pd.DataFrame(rows)
df.to_parquet(parquet_path, engine="pyarrow", index=False)
print(f"✅ 转换完成: {parquet_path}")
