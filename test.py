import numpy as np

norm = np.linalg.norm(((0, 0), (0, 2))) > np.linalg.norm(((0, 0), (0, 1)))

print(norm)