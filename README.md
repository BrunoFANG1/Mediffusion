# Mediffusion

Actively being documented. Please check back soon.

## Setup and Installation

### Step 1: Create a Conda Environment

If you haven't installed Conda yet, you can download it from [here](https://docs.anaconda.com/anaconda/install/). After installing, create a new Conda environment by running:

```bash
conda create --name mediffusion python=3.10
```

Activate the environment:

```bash
conda activate mediffusion
```

### Step 2: Install PyTorch

Install PyTorch specifically for CUDA 11.8 by running:

```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Step 3: Install The Package

You can install the latest version from github using:

```bash
pip install git+https://github.com/BardiaKh/Mediffusion.git -u
```

This will install all the necessary packages.

## Usage
## 1. Training Hyperparameters
Before starting the training, it is recommended that you set up some global constants and environment variables:

```python
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"
os.environ['WANDB_API_KEY'] = "WANDB-API-KEY"

TOTAL_IMAGE_SEEN = 40e6
BATCH_SIZE = 36
NUM_DEVICES = 2 # number of devices in CUDA_VISIBLE_DEVICES
TRAIN_ITERATIONS = int(TOTAL_IMAGE_SEEN / (BATCH_SIZE * NUM_DEVICES))
```

## 2. Preparing Data

To prepare the data, you need to create a dataset where each element is a dictionary. The dictionary should have the key "img" and may also contain additional keys like "cls" and "concat" depending on the type of condition. One way to do this is by using MONAI. Below is a sample code snippet:

```python
import monai as mn

train_data_dicts = [
    {"img": "./image1.dcm", "cls": 2},
    {"img": "./image2.dcm", "cls": 0}
]

valid_data_dicts = [
    {"img": "./image9.dcm", "cls": 1}
]

transforms = mn.transforms.Compose([
    mn.transforms.LoadImageD(keys="img"),
    mn.transforms.SelectItemsD(keys=["img","cls"]),
    mn.transforms.ToTensorD(keys=["img","cls"], dtype=torch.float, track_meta=False),
])

train_ds = Dataset(data=train_data_dicts, transform=transforms) 
valid_ds = Dataset(data=valid_data_dicts, transform=transforms)
train_sampler = torch.utils.data.RandomSampler(train_ds, replacement=True, num_samples=TOTAL_IMAGE_SEEN)
```

At the end of this step, you should have `train_ds`, `val_ds` and `train_sampler`.

## 3. Configuring Model

### Configuration Fields Explanation

Below is a table that provides descriptions for each element in the configuration file:

| Section    | Field                   | Description                                           |
|------------|-------------------------|-------------------------------------------------------|
| diffusion  | timesteps               | The number of timesteps in the diffusion process      |
|            | schedule_name           | The name of the schedule (e.g., "cosine")             |
|            | enforce_zero_terminal_snr | Whether to enforce zero terminal SNR (True/False)    |
|            | schedule_params         | Parameters related to the diffusion schedule          |
|            | -- beta_start           | Starting value for beta in the schedule               |
|            | -- beta_end             | Ending value for beta in the schedule                 |
|            | -- cosine_s             | Parameter for cosine schedule                         |
|            | timestep_respacing      | Can be a list of respacings. For example, with 200 steps, [10,20] means in the first 100, get 10 samples and in the next 100, get 20 samples. |
|            | mean_type               | Type of mean model (e.g., "VELOCITY")                 |
|            | var_type                | Type of variance model (e.g., "LEARNED_RANGE")        |
|            | loss_type               | The type of loss to use (e.g., "MSE")                 |
| optimizer  | lr                      | Learning rate                                         |
|            | type                    | The type of optimizer to use                          |
| validation | classifier_cond_scale   | Classifier guidance scale for validation logging.     |
|            | protocol                | Inference protocol for logging validation results     |
|            | log_original            | Whether to log the original validation data (True/False)         |
| model      | input_size              | The input size of the model. Can be an integer for square and cube images or a list of integers for specific axes, like [64, 64, 32] |
|            | dims                    | Number of dimensions, 2 or 3 for 2D and 3D images     |
|            | attention_resolutions   | List of resolutions for attention layers              |
|            | channel_mult            | List of multipliers for each layer's channels         |
|            | dropout                 | Dropout rate                                          |
|            | in_channels             | Number of input channels (image channels + concat channels) |
|            | out_channels            | Number of output channels (image channels or image channels * 2 if learning the variance) |
|            | model_channels          | Number of convolution channels in the model           |
|            | num_head_channels       | Number of attention head channels                     |
|            | num_heads               | Number of attention heads                             |
|            | num_heads_upsample      | Number of attention head after upsampling             |
|            | num_res_blocks          | List of the number of residual blocks for each layer  |
|            | resblock_updown         | Whether to use residual blocks for down/up sampling (True/False) |
|            | use_checkpoint          | Whether to use checkpointing (True/False)             |
|            | use_new_attention_order | Whether to use the new attention ordering (True/False) |
|            | use_scale_shift_norm    | Whether to use scale-shift normalization (True/False) |
|            | scale_skip_connection   | Whether to scaleskip connections (True/False)         |
|            | num_classes             | Number of classes for conditioning                    |
|            | concat_channels         | Number of concatenatong channels for conditioning (for super-resolution or inpainting) |
|            | guidance_drop_prob      | Drop probability for the classifier free guidance scale training |

For sample configurations, please checkout the `sample_configs` folder.

**Note**: If a field is left out of the config file, the default value is infered based on this file: `mediffusion/default_config/default.yaml`.

### Instantiating Model

You can instantiate the model using the configuration file and dataset as follows:

```python
from mediffusion import DiffusionModule

model = DiffusionModule(
    "./config.yaml",
    train_ds=train_ds,
    val_ds=valid_ds,
    dl_workers=2,
    train_sampler=train_sampler,
    batch_size=32,               # train batch size
    val_batch_size=16            # validation batch size (recommended size is half of batch_size)
)
```

## 4. Setting up Trainer
You can set up the trainer using the `Trainer` class:

```python
from mediffusion import Trainer

trainer = Trainer(
    max_steps=TRAIN_ITERATIONS,
    val_check_interval=5000,
    root_directory="./outputs", # where to save the weights and logs
    precision="16-mixed",       # mixed precision training
    devices=-1,                 # use all the devices in CUDA_VISIBLE_DEVICES
    nodes=1,
    wandb_project="Your_Project_Name",
    logger_instance="Your_Logger_Instance",
)
```

## 5. Train!

Finally, to train your model, you simply call:

```python
trainer.fit(model)
```

## Citation

If you find this work useful, please consider citing the parent project:

```
@article{KHOSRAVI2023107832,
    title = {Few-shot biomedical image segmentation using diffusion models: Beyond image generation},
    journal = {Computer Methods and Programs in Biomedicine},
    volume = {242},
    pages = {107832},
    year = {2023},
    issn = {0169-2607},
    doi = {https://doi.org/10.1016/j.cmpb.2023.107832},
    url = {https://www.sciencedirect.com/science/article/pii/S0169260723004984},
    author = {Bardia Khosravi and Pouria Rouzrokh and John P. Mickley and Shahriar Faghani and Kellen Mulford and Linjun Yang and A. Noelle Larson and Benjamin M. Howe and Bradley J. Erickson and Michael J. Taunton and Cody C. Wyles},
}
```