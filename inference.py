import os
import argparse
import multiprocessing

import torch
from data_loader.data_loader_inference import get_data_loaders
from model.model import RgbLidarFusion
from model.loss import YoloLoss
import numpy as np
from logging import getLogger
from tqdm import tqdm
import json
import matplotlib.pyplot as plt
from utils.kitti_viewer import show_lidar_with_boxes

# Enable TF32 for faster computation with less memory
torch.backends.cuda.matmul.allow_tf32 = True
torch.backends.cudnn.allow_tf32 = True

# Enable memory efficient attention
torch.backends.cuda.enable_mem_efficient_sdp(True)

# Set memory fraction (use 90% of available VRAM)
torch.cuda.set_per_process_memory_fraction(0.9, 0)

print("Memory optimizations enabled for RTX 4060")

SEED = 10
# Set the random seed manually for reproducibility.
np.random.seed(SEED)
torch.manual_seed(SEED)
if torch.cuda.is_available():
    torch.cuda.manual_seed(SEED)


def get_args(arg_list=None):
    parser = argparse.ArgumentParser(description='Hell Yeah')
    # setup params
    parser.add_argument('--data_dir', type=str, default="/mnt/fastDisk/kitti3d/kitti_object/testing")
    parser.add_argument('--output_dir', type=str, default="/mnt/fastDisk/kitti3d/kitti_object/testing/labels_2")
    parser.add_argument('--device', default=torch.device("cuda"))
    parser.add_argument('--num_data_loader_workers', type=int, default=multiprocessing.cpu_count())
    # monitor params
    parser.add_argument('--load_checkpoint', type=bool, default=False)
    parser.add_argument('--checkpoint_path', type=str, default="results/backup/checkpoint_epoch40.pth")
    parser.add_argument('--save_best_model', type=bool, default=False)
    parser.add_argument('--save_model_checkpoint', type=bool, default=True)
    parser.add_argument('--save_period', type=int, default=5)  # epoch
    parser.add_argument('--log_period', type=int, default=4)  # iteration
    parser.add_argument('--val_period', type=int, default=1000)  # epoch
    parser.add_argument('--use_wandb', type=bool, default=False)
    # data params
    parser.add_argument('--image_size', type=int, default=384)
    # training params
    parser.add_argument('--batch_size', type=int, default=2)
    parser.add_argument('--num_epochs', type=int, default=60)
    parser.add_argument('--lr', type=float, default=1e-2)
    parser.add_argument('--scheduler_step', type=int, default=10)
    parser.add_argument('--scheduler_gamma', type=float, default=0.1)
    # Pointcloud encoder params
    parser.add_argument('--pc_num_input_features', type=int, default=4)
    parser.add_argument('--pc_use_norm', type=bool, default=True)
    parser.add_argument('--pc_num_filters', type=list[int], default=[48, 96, 96]) #[64, 128, 128]) # [64, 128, 256]
    parser.add_argument('--pc_with_distance', type=bool, default=False)
    parser.add_argument('--pc_voxel_size', type=list[float], default=[0.32, 0.32, 4])
    parser.add_argument('--pc_range', type=list[float], default=[0, -60, -3, 120, 60, 1])
    parser.add_argument('--pc_max_num_voxels', type=int, default=8000)
    parser.add_argument('--pc_max_num_points_per_voxel', type=int, default=75)
    parser.add_argument('--pc_grid_size', type=list[int])
    # Yolo params
    parser.add_argument('--yolo_anchors', type=list[float], default=[1.56, 1.6, 3.9])  # h, w ,l
    parser.add_argument('--yolo_num_box_per_cell', type=int, default=1)  # use 1 for now to make it easy
    parser.add_argument('--yolo_box_length', type=int, default=9)  # conf, x, y, z, h, w, l, yaw_r, yaw_i
    # Validation params
    parser.add_argument('--visualize_sample', type=bool, default=False)
    parser.add_argument('--ori_img_h', type=int, default=375)
    parser.add_argument('--ori_img_w', type=int, default=1242)
    parser.add_argument('--inference_conf_threshold', type=float, default=0.5)
    parser.add_argument('--NMS_overlap_threshold', type=float, default=0.5)
    parser.add_argument('--MAP_overlap_threshold', type=float, default=0.5)
    args = parser.parse_args() if str is None else parser.parse_args(arg_list)
    return args

def save_predictions_to_file(predictions, output_path):
    """
    Save predictions in KITTI format to a text file
    
    Args:
        predictions: Tensor of shape (N, 16) with KITTI format labels
        output_path: Path to save the predictions
    """
    if predictions is None or len(predictions) == 0:
        # Create empty file if no predictions
        with open(output_path, 'w') as f:
            pass
        return
    
    with open(output_path, 'w') as f:
        for pred in predictions:
            # KITTI format: class truncated occluded alpha bbox_2d h w l x y z yaw score
            # We only have 3D info, so we use placeholder values for 2D bbox
            class_name = "Car"  # Assuming all predictions are cars
            truncated = 0.0
            occluded = 0
            alpha = -10  # Placeholder
            bbox_2d = "0 0 0 0"  # Placeholder
            
            h, w, l = pred[8].item(), pred[9].item(), pred[10].item()
            x, y, z = pred[11].item(), pred[12].item(), pred[13].item()
            yaw = pred[14].item()
            score = pred[15].item()
            
            line = f"{class_name} {truncated} {occluded} {alpha} {bbox_2d} "
            line += f"{h:.2f} {w:.2f} {l:.2f} {x:.2f} {y:.2f} {z:.2f} {yaw:.2f} {score:.4f}\n"
            f.write(line)
            f.flush()

def main(args):
    logger = getLogger(__name__)
    logger.info("Model set to evaluation mode")
    os.makedirs(args.output_dir, exist_ok=True)
    all_predictions = []
    test_loader = get_data_loaders(args)
    model = RgbLidarFusion(args).to(args.device)    
    checkpoint = torch.load(args.checkpoint_path, weights_only=False)
    model.load_state_dict(checkpoint['state_dict'])
    model.eval()
    
    loss_fn: YoloLoss = YoloLoss(args, args.pc_range, args.pc_voxel_size,
                                args.yolo_num_box_per_cell, args.yolo_box_length,
                                args.yolo_anchors)

    
    # Disable gradient computation for inference
    with torch.no_grad():
        logger.info("Starting inference pipeline")
        
        try:        
                for batch_idx, batch_data in enumerate(tqdm(test_loader)):
                    images = batch_data['image'].to(args.device)                    
                    lidars = batch_data['lidar']
                    calibs = batch_data['calib']
                    outputs = model(images, lidars) # Shape: (B, 9, H, W)
                    print("batch_idx: ", batch_idx)
                    print("batch_data keys: ", batch_data.keys())
                    print("image shape: ", batch_data['image'].shape)
                    print("lidar length: ", len(batch_data['lidar']))
                    print("shape:",outputs.shape)
                
                    for example_idx in range(outputs.shape[0]):
                        predictions = loss_fn.convert_yolo_output_to_kitti_labels(
                            outputs[example_idx], calibs[example_idx], conf_th=0.5)
                        logger.info(f"Predictions for sample {example_idx}: {predictions}")
                        #predictions[0].print_object()
                        
                        label_file = os.path.join(args.output_dir,
                                             f"{batch_idx:06d}.txt")
                        save_predictions_to_file(predictions, label_file)
                        #show_lidar_with_boxes(
                        #    lidars[example_idx],
                        #    predictions,
                        #    calibs[example_idx])
                
                logger.info("Inference completed for batch")

        except Exception as e:
            logger.error(f"Inference failed with error: {e}", exc_info=True)
            raise
        finally:
            logger.info("Inference completed")
            logger.info("Saving predictions to file")
            #with open(args.output_file, 'w') as f:
                #json.dump(all_predictions, f)
            logger.info("Predictions saved successfully")


if __name__ == '__main__':
    args = get_args()
    main(args)