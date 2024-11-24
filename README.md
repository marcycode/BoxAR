# BoxAR

BoxAR is an AR-based boxing game that helps you improve cardio and hand-eye coordination through punching and dodging. [improve description]

## Controls

- Left/Right Jab
- Dodge
- Block

## Tech Stack

- Uses a morphological skeleton in OpenCV to track user movement

## Conda environment setup

First, ensure you have conda installed. If not, you can download it from [here](https://docs.conda.io/en/latest/miniconda.html).

Then, create a new conda environment with the following command:

```bash
conda env create -f conda_env.yml
```

This will create a new environment called `boxar` with all the necessary dependencies. To activate the environment, run:

```bash
conda activate boxar
```

## Running Steps

- navigate to `boxAR-frontend` and run `npm run dev`
- in the main directory, run `flask run --port 8000`
