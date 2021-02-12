from __future__ import print_function
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from tools.lib.framereader import FrameReader, BaseFrameReader


class ToTensor(object):

    def __call__(self, sample):
        return {
            key: torch.from_numpy(value) for key, value in sample.items()
        }


class CommaDataset(Dataset):

    def __init__(self, main_dir, transform=None):
        self.main_dir = main_dir
        self.frame_reader = FrameReader(main_dir + 'video.hevc')

        self.gps_times = np.load(main_dir + 'global_pose/frame_gps_times')
        self.orientations = np.load(main_dir + 'global_pose/frame_orientations')
        self.positions = np.load(main_dir + 'global_pose/frame_positions')
        self.times = np.load(main_dir + 'global_pose/frame_times')
        self.velocities = np.load(main_dir + 'global_pose/frame_velocities')

        self.transform = transform

    def __len__(self):
        return len(self.velocities)

    def __getitem__(self, idx):
        image = np.array(self.frame_reader.get(idx, pix_fmt='rgb24')[0], dtype=np.float64)

        sample = {
            'image': image,
            'gps_times': self.gps_times,
            'orientations': self.orientations,
            'positions': self.positions,
            'times': self.times,
            'velocities': self.velocities[idx]
        }

        if self.transform:
            sample = self.transform(sample)

        return sample


if __name__ == "__main__":

    example_segment = 'Example_1/b0c9d2329ad1606b|2018-08-02--08-34-47/40/'
    frame_idx = 200

    comma_dataset = CommaDataset(main_dir=example_segment, transform=transforms.Compose([
        ToTensor()
    ]))

    comma_dataloader = DataLoader(comma_dataset, batch_size=4, shuffle=True, num_workers=0)

    # sample = comma_dataset[frame_idx]
    sample = next(iter(comma_dataloader))
    image = sample['image'][0].numpy()
    velocity = sample['velocities'][0].numpy()
