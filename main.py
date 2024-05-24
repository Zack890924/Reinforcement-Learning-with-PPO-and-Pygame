# Importing the optimzation frame - HPO
import optuna
# PPO algo for RL
from stable_baselines3 import PPO
# Bring in the eval policy method for metric calculation
from stable_baselines3.common.evaluation import evaluate_policy
# Import the sb3 monitor for logging 
from stable_baselines3.common.monitor import Monitor
# Import the vec wrappers to vectorize and frame stack
from stable_baselines3.common.vec_env import DummyVecEnv, VecFrameStack
# Import os to deal with filepaths
import os
from env import CustomEnv
from stable_baselines3.common.callbacks import BaseCallback

LOG_DIR = './logs/'
OPT_DIR = './opt/'

SAVE_PATH = os.path.join(OPT_DIR, 'trial_{}_best_model'.format(1))

def optimize_ppo(trial): 
    return {
        'n_steps':trial.suggest_int('n_steps', 2048, 8192),
        'gamma':trial.suggest_loguniform('gamma', 0.8, 0.9999),
        'learning_rate':trial.suggest_loguniform('learning_rate', 1e-5, 1e-4),
        'clip_range':trial.suggest_uniform('clip_range', 0.1, 0.4),
        'gae_lambda':trial.suggest_uniform('gae_lambda', 0.8, 0.99)
    }


def optimize_agent(trial):
    try:
        model_params = optimize_ppo(trial) 

        # Create environment 
        env = CustomEnv()
#         env = Monitor(env, LOG_DIR)
#         env = DummyVecEnv([lambda: env])
#         env = VecFrameStack(env, 4, channels_order='last')

        # Create algo 
        model = PPO('CnnPolicy', env, tensorboard_log=LOG_DIR, verbose=0, **model_params)
        model.learn(total_timesteps=100000)
        #model.learn(total_timesteps=100000)

        # Evaluate model 
#         mean_reward, _ = evaluate_policy(model, env, n_eval_episodes=5)
        mean_reward = 0
        for ep in range(5):
            obs = env.reset()
            total_reward = 0
            done = False
            while not done:
                action,_states = model.predict(obs)
                obs,reward,done,indo = env.step(action)
                total_reward+=reward
            mean_reward += total_reward
        mean_reward = mean_reward/5

        SAVE_PATH = os.path.join(OPT_DIR, 'trial_{}_best_model'.format(trial.number))
        model.save(SAVE_PATH)

        return mean_reward

    except Exception as e:
        return -1000


study = optuna.create_study(direction='maximize')
study.optimize(optimize_agent,n_trials=10,n_jobs=1)





class TrainAndLoggingCallback(BaseCallback):

    def __init__(self, check_freq, save_path, verbose=1):
        super(TrainAndLoggingCallback, self).__init__(verbose)
        self.check_freq = check_freq
        self.save_path = save_path

    def _init_callback(self):
        if self.save_path is not None:
            os.makedirs(self.save_path, exist_ok=True)

    def _on_step(self):
        if self.n_calls % self.check_freq == 0:
            model_path = os.path.join(self.save_path, 'best_model_{}'.format(self.n_calls))
            self.model.save(model_path)

        return True



env = CustomEnv()
env.reset()
CHECKPOINT_DIR = './train/'
callback = TrainAndLoggingCallback(check_freq=10000, save_path = CHECKPOINT_DIR)

# model = PPO('CnnPolicy',env,verbose=1,tensorboard_log=LOG_DIR,learning_rate=0.000001,n_steps=512)
# model.learn(total_timesteps=400000,callback=callback)
model = PPO('CnnPolicy',env,verbose=1,tensorboard_log=LOG_DIR,learning_rate=8.484748038245596e-06,n_steps=5248,clip_range=0.10259838130818061,gae_lambda=0.9314787326141037,gamma=0.931478732614103)
model.load(os.path.join(OPT_DIR, 'trial_4_best_model.zip'))
model.learn(total_timesteps=300000, callback=callback)