# BoxAR

BoxAR is an AR-based boxing game that helps you improve cardio and hand-eye coordination through punching and dodging. Play in 4 different modes!
- Free Play: Practice your punches, dodges and timing!
- Scoring Mode: Follow the prompts to punch and dodge your way to a high score!
- Survival: Punch and dodge as long as you can!
- Multiplayer: Compete with a friend in a 1v1 match!

<p align="center">
  <img src="frontend/public/boxar-logo-dark.png" />
</p>


## Controls

- Left/Right Jab
- Dodge
- Block

## Tech Stack

- Uses a morphological skeleton in OpenCV to track user movement and determine punches and dodges
- Client webview is built with React.js
- Video is streamed to the client using Flask

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

Then, install the necessary python dependencies with:

```bash
pip install -r requirements.txt
```

## Running Steps

- navigate to `boxAR-frontend` and run `npm run dev` (also run `npm install` if you haven't already)
- in the main directory, run `flask run --port 8000`
