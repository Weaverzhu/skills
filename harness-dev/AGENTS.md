# Harness dev

This folder maintain a skill for agent harness development, using a simple feedback and then iterate loop.

## Loop structure

1. Make sure the implementation support export the raw trajectories for furthur examination. If not, ask the user for help and work on them first.
2. Get some trajectories, could be running the trajectories maintained by the repo yourself, or provided by user if the trajectories are not convenient to be run by codex.
3. Examine the trajectories, do some analysis. You should find a workspace for saving some scripts or tools when looking at the trajectories, and explain your examine ideas and conclusions to the user. Finally you may come up some ideas for furthur development. A simple example of development could be trimming LLM input to save tokens, or providing more context or info to the LLM.
4. If user let you do the loop multiple times, start over the loop again, otherwise show conclusions to the users.
