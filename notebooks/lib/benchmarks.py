import coordinates as coord
import numpy as np
from tqdm import tqdm


def get_altitude_errors(frame_poss):
  '''
  Takes in a list of 2D arrays. Where every element
  of the list represents all the frame positions
  of a segment in ECEF.
  '''

  # set size of squares (bins) of road which we
  # assume to the road to have constant height
  # and area within which to check
  local = coord.LocalCoord.from_ecef([-2712470.27794758, -4262442.18438959, 3879912.32221487])
  north_bounds = [-16000, 2500]
  east_bounds = [-1000, 7000]
  binsize = 5
  north_bins, east_bins = [], []
  for i in xrange(north_bounds[0], north_bounds[1], binsize):
    north_bins.append([i,i+binsize])
  for i in xrange(east_bounds[0], east_bounds[1], binsize):
    east_bins.append([i,i+binsize])

  # convert positions to NED
  frame_poss_ned = []
  for pos in frame_poss:
    if pos is None:
      continue
    frame_poss_ned.append(local.ecef2ned(pos))

  # find bin idxs for all frame positions
  bins = [[[] for j in xrange(len(east_bins))] for i in xrange(len(north_bins))]
  for pos_ned in frame_poss_ned:
    north_idxs = np.clip(((pos_ned[:,0] - north_bounds[0])/binsize).astype(int),
                         0,
                         len(bins)-1)
    east_idxs = np.clip(((pos_ned[:,1] - east_bounds[0])/binsize).astype(int),
                        0,
                        len(bins[0])-1)
    idxs = np.column_stack((north_idxs, east_idxs))
    _, uniq = np.unique(idxs, return_index=True, axis=0)
    for p, idx in zip(pos_ned[uniq], idxs[uniq]):
      bins[idx[0]][idx[1]].append(p)


  # Now find the errors by looking at the deviation
  # from the mean in each bin
  alt_diffs = []
  k = 0
  for pos_ned in tqdm(frame_poss_ned):
    k +=1
    north_idxs = np.clip(((pos_ned[:,0] - north_bounds[0])/binsize).astype(int),
                         0,
                         len(bins)-1)
    east_idxs = np.clip(((pos_ned[:,1] - east_bounds[0])/binsize).astype(int),
                        0,
                        len(bins[0])-1)
    idxs = np.column_stack((north_idxs, east_idxs))
    alt_diffs.append([])
    for p, idx in zip(pos_ned, idxs):
      # we want at least 5 observations per bin
      if len(bins[idx[0]][idx[1]]) > 5:
        alt_diffs[-1].append(p[2] - np.mean(np.array(bins[idx[0]][idx[1]])[:,2]))
  return alt_diffs
