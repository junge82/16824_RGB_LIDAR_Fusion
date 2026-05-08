# create_split.py
import random

indices = list(range(7481))
random.shuffle(indices)

train_size = int(0.8 * len(indices))
train_indices = indices[:train_size]
val_indices = indices[train_size:]

with open('train_split.txt', 'w') as f:
    f.write('\n'.join(map(str, train_indices)))

with open('val_split.txt', 'w') as f:
    f.write('\n'.join(map(str, val_indices)))

print(f"Train: {len(train_indices)}, Val: {len(val_indices)}")