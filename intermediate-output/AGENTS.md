# Intermediate output


When developing large apps, or it is often expensive to run the full code, we use the strategy that expose the output of a module to make it easy to check the intermediate results.

We check each small module separately so we control the complexity of debugging and reading feedback/output.

This skill should only be invoked explicitly by user.

Provide a `./sync.sh` script to sync skills under `skills/` to my global skills folder for claude-code and code.
