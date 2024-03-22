import os
import sys
import numpy as np
import scipy
import matplotlib.pyplot as plt

example_segment = '../comma2k/Chunk_1/b0c9d2329ad1606b|2018-08-17--12-07-08'

sys.path.append('..')
os.listdir(example_segment) # all the files present for every minute of driving
# We can plot the speed from a variety of sources
plt.figure(figsize = (12, 12))

# from can data
plt.plot(np.load(example_segment + '/28/processed_log/CAN/speed/t'),
     np.load(example_segment + '/28/processed_log/CAN/speed/value'),
     label='CAN')

# from qcom gnss data
plt.plot(np.load(example_segment + '/28/processed_log/GNSS/live_gnss_qcom/t'),
     np.load(example_segment + '/28/processed_log/GNSS/live_gnss_qcom/value')[:,2],
          label='live qcom fix')

# from u-blox gnss data
plt.plot(np.load(example_segment + '/28/processed_log/GNSS/live_gnss_ublox/t'),
     np.load(example_segment + '/28/processed_log/GNSS/live_gnss_ublox/value')[:,2],
     label='live u-blox live fix')

# from post-processed data
plt.plot(np.load(example_segment + '/28/global_pose/frame_times'),
     np.linalg.norm(np.load(example_segment + '/28/global_pose/frame_velocities'),axis=1), linewidth=4,
     label='post-processed poses')

plt.title('Speed from various sources', fontsize=25)
plt.legend(fontsize=25)
plt.xlabel('boot time (s)', fontsize=18)
plt.ylabel('speed (m/s)', fontsize=18)
plt.show()